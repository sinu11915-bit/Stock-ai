import os
import io
import re
import json
import random
import hashlib
import urllib.request
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Avika.Ai - Multi-User Platform")

# PASSWORD HASHING
def hash_pass(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

# DATABASE SETUP
def get_db():
    conn = sqlite3.connect("users.db", timeout=15)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                name TEXT,
                email TEXT UNIQUE,
                phone TEXT UNIQUE,
                password TEXT
            )
        """)
        conn.commit()

init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# AUTH MODELS
class RegisterReq(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class LoginReq(BaseModel):
    identifier: str
    password: str

@app.post("/api/register")
def register(data: RegisterReq):
    try:
        with get_db() as conn:
            c = conn.cursor()
            # Generate pure numerical random 6-digit User ID (e.g. 849201)
            random_num_id = str(random.randint(100000, 999999))
            
            hashed = hash_pass(data.password)
            c.execute(
                "INSERT INTO users (user_id, name, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                (random_num_id, data.name.strip(), data.email.strip().lower(), data.phone.strip(), hashed)
            )
            conn.commit()
            return {
                "message": "Registration successful! Ab login karein.",
                "user": {
                    "name": data.name.strip(),
                    "email": data.email.strip().lower(),
                    "phone": data.phone.strip(),
                    "user_id": random_num_id
                }
            }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Yeh Email ya Mobile Number pehle se registered hai!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/login")
def login(data: LoginReq):
    try:
        ident = data.identifier.strip().lower()
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT user_id, name, email, phone, password FROM users WHERE email=? OR phone=?",
                (ident, data.identifier.strip())
            )
            user = c.fetchone()
            
            if not user or user[4] != hash_pass(data.password):
                raise HTTPException(status_code=400, detail="Galat Email/Mobile ya Password!")
            
            return {
                "message": "Login successful!",
                "user": {
                    "user_id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "phone": user[3]
                }
            }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# GROQ LLM ENGINE (llama-3.1-8b-instant with Browser Headers)
def call_avika_brain(prompt: str):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    current_date = now_ist.strftime("%d %B %Y")
    current_time = now_ist.strftime("%I:%M %p")
    current_day = now_ist.strftime("%A")

    system_instruction = f"""
    Aap Avika.Ai hain — ek super-intelligent, helpful Indian AI Assistant aur Stock Market Analyst.
    
    Live Reality Context:
    - Current Location: India
    - Current Indian Date (IST): {current_date} ({current_day})
    - Current Indian Time (IST): {current_time}
    - Deepawali (Diwali) 2026: 8 November 2026 (Sunday), Kartik Maas Amavasya.
    - Market Baseline: Nifty 50 (~22,750), Bank Nifty (~54,360), Sensex (~74,820), Tata Steel (~154.50).

    Rules:
    1. Agar stock market (Nifty, Bank Nifty, Sensex, Tata Steel) puche toh exact Buy Entry, Stop Loss (SL) aur Target 1 & 2 dein.
    2. Agar maths (+, -, *, ×, /, %, √) puche: exact answer calculate karein.
    3. Agar dates ya calendar puche: upar diye Indian date ke hisab se exact batayein.
    4. User ki bhasha (Hindi, Hinglish, Bengali, English) me natural aur friendly jawab dein.
    5. Kabhi 'I cannot provide that' bolkar mana na karein.
    """

    if not api_key:
        return "⚠️ GROQ_API_KEY Render par configure nahi hai! Kripya Render Environment me GROQ_API_KEY check karein."

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Error: {str(e)}"

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    user_query = prompt.strip() if prompt else "Nifty analysis"
    ans = call_avika_brain(user_query)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Avika.Ai - Trading & AI Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <style>
            .no-scrollbar::-webkit-scrollbar { display: none; }
            .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body class="bg-[#030611] text-slate-100 min-h-screen font-sans flex flex-col justify-between relative overflow-x-hidden">
        
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none"></div>

        <!-- AUTH SCREEN (REGISTER / LOGIN) - SHOWN FIRST TO NEW USERS -->
        <div id="authScreen" class="fixed inset-0 bg-[#030611] z-50 flex items-center justify-center p-4 overflow-y-auto">
            <div class="bg-slate-900/95 border border-slate-800 rounded-3xl p-6 w-full max-w-sm shadow-2xl backdrop-blur-xl my-auto">
                
                <div class="text-center mb-6">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-2xl mb-2">
                        <i class="fa-solid fa-sparkles"></i>
                    </div>
                    <h2 class="text-xl font-extrabold text-white">Avika.Ai</h2>
                    <p class="text-xs text-slate-400 mt-1">Trading Terminal & Smart AI</p>
                </div>

                <!-- TABS (LOGIN / REGISTER) -->
                <div class="flex border-b border-slate-800 mb-5">
                    <button id="tabBtnLogin" onclick="switchAuthTab('login')" class="flex-1 pb-2 text-xs font-bold text-emerald-400 border-b-2 border-emerald-400">Login</button>
                    <button id="tabBtnReg" onclick="switchAuthTab('reg')" class="flex-1 pb-2 text-xs font-semibold text-slate-400">Register</button>
                </div>

                <!-- LOGIN FORM -->
                <div id="formLogin" class="space-y-3.5">
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Email ya Mobile Number</label>
                        <input id="lIdentifier" type="text" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="user@gmail.com ya 9876543210">
                    </div>
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Password</label>
                        <input id="lPassword" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="••••••••">
                    </div>
                    <button id="btnDoLogin" onclick="handleLogin()" class="w-full mt-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black py-3 rounded-xl text-xs uppercase tracking-wider transition shadow-lg">Login Karein</button>
                </div>

                <!-- REGISTER FORM -->
                <div id="formReg" class="space-y-3 hidden">
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Aapka Pura Naam (Full Name)</label>
                        <input id="rName" type="text" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="Rahul Sharma">
                    </div>
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Mobile Number</label>
                        <input id="rPhone" type="tel" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="9876543210">
                    </div>
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Email Address</label>
                        <input id="rEmail" type="email" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="user@gmail.com">
                    </div>
                    <div>
                        <label class="text-[11px] text-slate-400 font-medium">Password Banayein</label>
                        <input id="rPassword" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="••••••••">
                    </div>
                    <button id="btnDoReg" onclick="handleRegister()" class="w-full mt-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black py-3 rounded-xl text-xs uppercase tracking-wider transition shadow-lg">Register Karein</button>
                </div>

            </div>
        </div>

        <!-- 3-LINE SIDEBAR DRAWER (SHOWS LOGGED-IN USER'S OWN DETAILS) -->
        <div id="drawerOverlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 hidden transition-opacity"></div>
        <div id="sidebarDrawer" class="fixed top-0 left-0 h-full w-80 bg-slate-900/98 border-r border-slate-800 p-5 z-50 transform -translate-x-full transition-transform duration-300 flex flex-col justify-between shadow-2xl backdrop-blur-xl overflow-y-auto">
            <div>
                <div class="flex justify-between items-center pb-4 border-b border-slate-800">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid fa-sparkles text-emerald-400 text-xl"></i>
                        <span class="font-extrabold text-base text-white">Avika.Ai Menu</span>
                    </div>
                    <button onclick="toggleMenu()" class="text-slate-400 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
                </div>

                <!-- USER PROFILE CARD (DYNAMICALLY FILLED) -->
                <div class="mt-4 p-4 bg-slate-950/80 rounded-2xl border border-slate-800 space-y-1.5 shadow-inner">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Account Profile</span>
                        <span class="text-[9px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-bold">Online</span>
                    </div>
                    <p id="profName" class="text-sm font-bold text-white truncate">-</p>
                    <p class="text-xs font-mono text-slate-300">User ID: <span id="profUserId" class="text-emerald-400 font-extrabold tracking-wider">000000</span></p>
                    <p id="profEmail" class="text-[11px] text-slate-400 truncate mt-0.5">-</p>
                    <p id="profPhone" class="text-[11px] text-slate-400">-</p>
                </div>

                <!-- MENU LIST -->
                <div class="mt-4 space-y-2 text-xs font-semibold">
                    <button onclick="alert('Wallet Balance: ₹0.00')" class="w-full flex items-center justify-between p-3 bg-slate-950/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-200">
                        <div class="flex items-center space-x-2.5"><i class="fa-solid fa-wallet text-violet-400"></i><span>Wallet & Recharge</span></div>
                        <span class="text-[10px] bg-violet-500/20 text-violet-300 px-2 py-0.5 rounded-lg">₹0.00</span>
                    </button>
                    <button onclick="alert('Pro Membership activated for testing!')" class="w-full flex items-center justify-between p-3 bg-gradient-to-r from-amber-500/20 to-yellow-500/20 rounded-xl border border-amber-500/30 text-amber-300">
                        <div class="flex items-center space-x-2.5"><i class="fa-solid fa-crown text-amber-400"></i><span>Upgrade Pro (₹29)</span></div>
                        <span class="text-[9px] bg-amber-500/30 text-amber-200 px-1.5 py-0.5 rounded-md font-bold">VIP</span>
                    </button>
                    <button onclick="alert('Support Bot Active: Ticket Created'); toggleMenu()" class="w-full flex items-center space-x-2.5 p-3 bg-slate-950/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-200">
                        <i class="fa-solid fa-headset text-emerald-400"></i><span>Customer Support</span>
                    </button>
                </div>
            </div>

            <!-- LOGOUT -->
            <button onclick="handleLogout()" class="w-full mt-4 flex items-center justify-center space-x-2 p-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl text-xs font-bold transition">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
                <span>Logout Account</span>
            </button>
        </div>

        <!-- TOP HEADER -->
        <header id="mainHeader" class="sticky top-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-b border-slate-800/80 px-4 py-2.5 hidden">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2.5">
                    <button onclick="toggleMenu()" class="text-slate-300 hover:text-emerald-400 text-lg p-2 rounded-xl bg-slate-900 border border-slate-800 shadow">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <div class="flex items-center space-x-1.5">
                        <i class="fa-solid fa-sparkles text-emerald-400 text-lg animate-pulse"></i>
                        <h1 class="text-base font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Avika.Ai</h1>
                    </div>
                </div>

                <div class="flex items-center space-x-2">
                    <button onclick="alert('VIP Pro Active (₹29)')" class="text-[10px] bg-gradient-to-r from-amber-500 to-yellow-500 text-slate-950 font-black px-2.5 py-1.5 rounded-xl shadow">
                        👑 ₹29
                    </button>
                    <button onclick="stopAudio()" title="Stop Voice" class="text-xs bg-red-950/60 border border-red-800 text-red-400 p-1.5 px-2 rounded-xl">
                        <i class="fa-solid fa-volume-xmark"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- MAIN SCREENS (TABS) -->
        <main id="mainContent" class="flex-1 max-w-md w-full mx-auto p-4 pb-28 overflow-y-auto hidden">
            
            <!-- TAB 1: HOME PAGE -->
            <section id="secHome" class="space-y-4">
                <div class="p-4 bg-gradient-to-r from-amber-500/20 via-yellow-500/10 to-transparent border border-amber-500/40 rounded-3xl shadow-lg flex justify-between items-center">
                    <div>
                        <span class="text-[9px] bg-amber-400 text-slate-950 font-black px-2 py-0.5 rounded-md uppercase">VIP Access</span>
                        <h2 class="text-sm font-extrabold text-white mt-1">Avika.Ai Pro Membership</h2>
                        <p class="text-[11px] text-slate-300">Live Indian Charts & AI Accuracy</p>
                    </div>
                    <span class="bg-amber-400 text-slate-950 font-black text-xs px-3 py-1.5 rounded-xl">₹29</span>
                </div>

                <div>
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Indian Markets Watchlist</h3>
                    <div class="grid grid-cols-2 gap-2.5 text-xs">
                        <div onclick="switchTab('charts', 'NSE:NIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>NIFTY 50</span><span class="text-emerald-400">▲ +0.68%</span></div>
                            <p class="text-base font-black text-white mt-1">₹22,753.20</p>
                        </div>
                        <div onclick="switchTab('charts', 'BSE:SENSEX')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>SENSEX</span><span class="text-emerald-400">▲ +0.55%</span></div>
                            <p class="text-base font-black text-white mt-1">₹74,820.00</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:BANKNIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>BANK NIFTY</span><span class="text-emerald-400">▲ +0.45%</span></div>
                            <p class="text-base font-black text-white mt-1">₹54,366.70</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:TATASTEEL')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>TATA STEEL</span><span class="text-emerald-400">▲ +1.20%</span></div>
                            <p class="text-base font-black text-white mt-1">₹154.50</p>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-900/80 border border-slate-800 rounded-3xl flex justify-between items-center">
                    <div>
                        <h4 class="text-xs font-bold text-white">Live Candlestick Charts</h4>
                        <p class="text-[11px] text-slate-400">All Indian Stocks, Indicators & Fullscreen</p>
                    </div>
                    <button onclick="switchTab('charts', 'NSE:NIFTY')" class="bg-emerald-500 text-slate-950 font-bold text-xs px-3 py-2 rounded-xl">Open Charts 📈</button>
                </div>
            </section>

            <!-- TAB 2: AI CHAT (GROQ REAL AI) -->
            <section id="secChat" class="hidden space-y-4">
                <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                    <i class="fa-solid fa-bolt text-amber-400 text-xs mt-0.5"></i>
                    <p class="text-[10px] text-amber-200/90 leading-tight">
                        <strong>Avika AI:</strong> Sensex, Nifty, Deepawali date, ya koi bhi sawal puchiye!
                    </p>
                </div>
                <div id="chatFeed" class="space-y-3">
                    <div class="flex items-start space-x-2.5">
                        <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                            <i class="fa-solid fa-sparkles"></i>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                            Hello! Main **Avika.Ai** hoon. 💬<br>
                            SENSEX, NIFTY prediction, Maths, Dates ya koi bhi sawal poochiye!
                        </div>
                    </div>
                </div>
            </section>

            <!-- TAB 3: LIVE CHARTS -->
            <section id="secCharts" class="hidden space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-xs font-bold text-white flex items-center">
                        <i class="fa-solid fa-chart-line text-emerald-400 mr-2"></i> Live Candlestick Broker Chart
                    </h3>
                    <button onclick="toggleFullScreen()" class="text-xs bg-slate-900 border border-slate-700 text-emerald-400 px-2.5 py-1.5 rounded-xl font-bold flex items-center shadow">
                        <i class="fa-solid fa-expand mr-1.5"></i> Fullscreen
                    </button>
                </div>

                <div class="flex space-x-2 overflow-x-auto no-scrollbar py-1 text-xs">
                    <button onclick="renderChart('NSE:NIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">NIFTY</button>
                    <button onclick="renderChart('BSE:SENSEX')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">SENSEX</button>
                    <button onclick="renderChart('NSE:BANKNIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">BANK NIFTY</button>
                    <button onclick="renderChart('NSE:TATASTEEL')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">TATA STEEL</button>
                    <button onclick="renderChart('NSE:RELIANCE')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">RELIANCE</button>
                </div>

                <div id="chartWrapper" class="h-[440px] bg-slate-950 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative">
                    <div id="tv_chart_container" class="w-full h-full"></div>
                </div>

                <button onclick="predictCurrentChart()" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black py-3 rounded-2xl text-xs shadow-lg transition">
                    ⚡ AI Predict This Live Chart
                </button>
            </section>

        </main>

        <!-- CHAT INPUT BAR -->
        <div id="chatControls" class="hidden fixed bottom-14 left-0 right-0 max-w-md mx-auto p-2.5 bg-[#070b16]/95 backdrop-blur-xl border-t border-slate-800/80 z-20">
            <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition">
                <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Sensex, Nifty buy/sell, 2×2, date..." onkeydown="if(event.key==='Enter') sendChat()">
                <button id="micBtn" onclick="toggleSpeech()" class="text-emerald-400 hover:text-emerald-300 p-2 text-base transition">
                    <i class="fa-solid fa-microphone"></i>
                </button>
                <button id="sendBtn" onclick="sendChat()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2 px-3 rounded-xl text-xs transition">
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
            </div>
        </div>

        <!-- BOTTOM NAVIGATION TABS -->
        <nav id="bottomNav" class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16] border-t border-slate-800 px-6 py-2 hidden">
            <div class="max-w-md mx-auto flex justify-between items-center text-center">
                <button id="navHome" onclick="switchTab('home')" class="flex flex-col items-center text-emerald-400 transition">
                    <i class="fa-solid fa-house text-base"></i>
                    <span class="text-[10px] font-bold mt-0.5">Home</span>
                </button>
                <button id="navChat" onclick="switchTab('chat')" class="flex flex-col items-center text-slate-500 hover:text-emerald-400 transition">
                    <i class="fa-solid fa-comment-dots text-base"></i>
                    <span class="text-[10px] font-bold mt-0.5">AI Chat</span>
                </button>
                <button id="navCharts" onclick="switchTab('charts')" class="flex flex-col items-center text-slate-500 hover:text-emerald-400 transition">
                    <i class="fa-solid fa-chart-candlestick text-base"></i>
                    <span class="text-[10px] font-bold mt-0.5">Live Charts</span>
                </button>
            </div>
        </nav>

        <script>
            let currentSymbol = 'NSE:NIFTY';
            let activeTab = 'home';
            let recognition = null;
            let currentUtterance = null;

            // AUTH STATE CHECK
            function checkAuthState() {
                const rawUser = localStorage.getItem('avika_user');
                if (rawUser) {
                    const u = JSON.parse(rawUser);
                    document.getElementById('authScreen').classList.add('hidden');
                    document.getElementById('mainHeader').classList.remove('hidden');
                    document.getElementById('mainContent').classList.remove('hidden');
                    document.getElementById('bottomNav').classList.remove('hidden');

                    // Populate drawer with user's own details
                    document.getElementById('profName').innerText = u.name || 'User';
                    document.getElementById('profUserId').innerText = u.user_id || '000000';
                    document.getElementById('profEmail').innerText = u.email || '-';
                    document.getElementById('profPhone').innerText = 'Mob: +91 ' + (u.phone || '-');
                } else {
                    document.getElementById('authScreen').classList.remove('hidden');
                    document.getElementById('mainHeader').classList.add('hidden');
                    document.getElementById('mainContent').classList.add('hidden');
                    document.getElementById('bottomNav').classList.add('hidden');
                }
            }

            function switchAuthTab(tab) {
                if (tab === 'login') {
                    document.getElementById('formLogin').classList.remove('hidden');
                    document.getElementById('formReg').classList.add('hidden');
                    document.getElementById('tabBtnLogin').className = "flex-1 pb-2 text-xs font-bold text-emerald-400 border-b-2 border-emerald-400";
                    document.getElementById('tabBtnReg').className = "flex-1 pb-2 text-xs font-semibold text-slate-400";
                } else {
                    document.getElementById('formLogin').classList.add('hidden');
                    document.getElementById('formReg').classList.remove('hidden');
                    document.getElementById('tabBtnReg').className = "flex-1 pb-2 text-xs font-bold text-emerald-400 border-b-2 border-emerald-400";
                    document.getElementById('tabBtnLogin').className = "flex-1 pb-2 text-xs font-semibold text-slate-400";
                }
            }

            async function handleRegister() {
                const name = document.getElementById('rName').value.trim();
                const phone = document.getElementById('rPhone').value.trim();
                const email = document.getElementById('rEmail').value.trim();
                const password = document.getElementById('rPassword').value.trim();

                if (!name || !phone || !email || !password) {
                    return alert("Sabhi details bharna zaroori hai!");
                }

                const btn = document.getElementById('btnDoReg');
                btn.disabled = true;
                btn.innerText = "Registering...";

                try {
                    const res = await fetch('/api/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ name, email, phone, password })
                    });
                    const d = await res.json();
                    if (res.ok) {
                        alert(d.message + " Aapka Random User ID hai: " + d.user.user_id);
                        localStorage.setItem('avika_user', JSON.stringify(d.user));
                        checkAuthState();
                    } else {
                        alert(d.detail || "Registration failed!");
                    }
                } catch (e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Register Karein";
                }
            }

            async function handleLogin() {
                const identifier = document.getElementById('lIdentifier').value.trim();
                const password = document.getElementById('lPassword').value.trim();

                if (!identifier || !password) {
                    return alert("Email/Mobile aur Password bharein!");
                }

                const btn = document.getElementById('btnDoLogin');
                btn.disabled = true;
                btn.innerText = "Logging in...";

                try {
                    const res = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ identifier, password })
                    });
                    const d = await res.json();
                    if (res.ok) {
                        localStorage.setItem('avika_user', JSON.stringify(d.user));
                        checkAuthState();
                    } else {
                        alert(d.detail || "Login failed!");
                    }
                } catch (e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Login Karein";
                }
            }

            function handleLogout() {
                localStorage.removeItem('avika_user');
                toggleMenu();
                checkAuthState();
            }

            function toggleMenu(){
                const drawer = document.getElementById('sidebarDrawer');
                const overlay = document.getElementById('drawerOverlay');
                drawer.classList.toggle('-translate-x-full');
                overlay.classList.toggle('hidden');
            }

            function toggleModal(id){
                const m = document.getElementById(id);
                if (m) m.classList.toggle('hidden');
            }

            function toggleFullScreen(){
                const elem = document.getElementById('chartWrapper');
                if (!document.fullscreenElement) {
                    if (elem.requestFullscreen) elem.requestFullscreen();
                    else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                } else {
                    if (document.exitFullscreen) document.exitFullscreen();
                }
            }

            function switchTab(tab, symbol){
                activeTab = tab;
                document.getElementById('secHome').classList.add('hidden');
                document.getElementById('secChat').classList.add('hidden');
                document.getElementById('secCharts').classList.add('hidden');
                document.getElementById('chatControls').classList.add('hidden');

                document.getElementById('navHome').className = "flex flex-col items-center text-slate-500";
                document.getElementById('navChat').className = "flex flex-col items-center text-slate-500";
                document.getElementById('navCharts').className = "flex flex-col items-center text-slate-500";

                if(tab === 'home'){
                    document.getElementById('secHome').classList.remove('hidden');
                    document.getElementById('navHome').className = "flex flex-col items-center text-emerald-400";
                } else if(tab === 'chat'){
                    document.getElementById('secChat').classList.remove('hidden');
                    document.getElementById('chatControls').classList.remove('hidden');
                    document.getElementById('navChat').className = "flex flex-col items-center text-emerald-400";
                } else if(tab === 'charts'){
                    document.getElementById('secCharts').classList.remove('hidden');
                    document.getElementById('navCharts').className = "flex flex-col items-center text-emerald-400";
                    renderChart(symbol || currentSymbol);
                }
            }

            function renderChart(sym){
                currentSymbol = sym;
                new TradingView.widget({
                    "autosize": true,
                    "symbol": sym,
                    "interval": "5",
                    "timezone": "Asia/Kolkata",
                    "theme": "dark",
                    "style": "1",
                    "locale": "in",
                    "toolbar_bg": "#070b16",
                    "enable_publishing": false,
                    "allow_symbol_change": true,
                    "container_id": "tv_chart_container"
                });
            }

            function predictCurrentChart(){
                const name = currentSymbol.replace('NSE:', '').replace('BSE:', '');
                switchTab('chat');
                document.getElementById('promptInput').value = name + ' ka live analysis aur prediction batao';
                sendChat();
            }

            function stopAudio(){
                if('speechSynthesis' in window) window.speechSynthesis.cancel();
            }

            function speak(text){
                stopAudio();
                const clean = text.replace(/[*#•_>~`\-]/g, ' ').replace(/\\s+/g, ' ');
                currentUtterance = new SpeechSynthesisUtterance(clean);
                currentUtterance.lang = 'hi-IN';
                currentUtterance.rate = 0.85;
                window.speechSynthesis.speak(currentUtterance);
            }

            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRec();
                recognition.lang = 'hi-IN';
                recognition.onresult = function(e){
                    document.getElementById('promptInput').value = e.results[0][0].transcript;
                    sendChat();
                };
            }

            function toggleSpeech(){
                if(recognition) recognition.start();
                else alert("Voice recognition not supported!");
            }

            async function sendChat(){
                const input = document.getElementById('promptInput');
                const prompt = input.value.trim();
                if(!prompt) return;

                const feed = document.getElementById('chatFeed');
                input.value = '';

                feed.insertAdjacentHTML('beforeend', `
                    <div class="flex justify-end">
                        <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-2xl rounded-tr-sm p-3 text-xs max-w-[85%] shadow-md">
                            ${prompt}
                        </div>
                    </div>
                `);

                const tempId = 'temp_' + Date.now();
                feed.insertAdjacentHTML('beforeend', `
                    <div id="${tempId}" class="flex items-center space-x-2 text-[11px] text-emerald-400 font-bold bg-slate-900 border border-emerald-500/30 p-2.5 rounded-2xl max-w-[200px] animate-pulse">
                        <i class="fa-solid fa-bolt fa-spin"></i>
                        <span>Avika is answering... ⚡</span>
                    </div>
                `);

                try {
                    const fd = new FormData();
                    fd.append('prompt', prompt);
                    const res = await fetch('/api/analyze', { method: 'POST', body: fd });
                    const d = await res.json();
                    
                    document.getElementById(tempId).remove();
                    feed.insertAdjacentHTML('beforeend', `
                        <div class="flex items-start space-x-2.5">
                            <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                                <i class="fa-solid fa-sparkles"></i>
                            </div>
                            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 max-w-[88%] shadow-xl leading-relaxed whitespace-pre-wrap">
                                <div>${d.analysis}</div>
                                <button onclick="speak(this.previousElementSibling.innerText)" class="mt-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-emerald-400 px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center transition shadow">
                                    <i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein
                                </button>
                            </div>
                        </div>
                    `);
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                } catch(e){
                    if(document.getElementById(tempId)) document.getElementById(tempId).remove();
                    alert("Error: " + e.message);
                }
            }

            // ON PAGE LOAD CHECK AUTH
            checkAuthState();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
