import os
import io
import sqlite3
import hashlib
import base64
import json
import time
import urllib.request
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image
from pydantic import BaseModel

app = FastAPI(title="NiftyLens AI Ultra")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect("users.db", timeout=20)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                phone TEXT UNIQUE,
                password TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                email TEXT,
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

class RegisterData(BaseModel):
    email: str
    phone: str
    password: str

class LoginData(BaseModel):
    identifier: str
    password: str

class SupportData(BaseModel):
    user_id: str
    email: str
    message: str

@app.post("/api/register")
def register(data: RegisterData):
    try:
        with get_db() as conn:
            c = conn.cursor()
            hashed = hash_password(data.password)
            c.execute("INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
                      (data.email.strip().lower(), data.phone.strip(), hashed))
            conn.commit()
            uid = f"NL-{c.lastrowid:04d}"
            return {"message": "Registration successful! Ab Login karein.", "user_id": uid}
    except sqlite3.IntegrityError:
        return {"message": "Pehle se registered hai! Aap direct login kar sakte hain.", "user_id": "NL-USER"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/login")
def login(data: LoginData):
    ident = data.identifier.strip().lower()
    
    # PERMANENT AUTO-LOGIN FOR MASTER USER (Never gets deleted by Render!)
    if "sinu11915" in ident or "6290565859" in ident:
        return {
            "token": "authenticated_master",
            "email": "sinu11915@gmail.com",
            "phone": "6290565859",
            "user_id": "NL-PRO-01"
        }
    
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id, email, phone, password FROM users WHERE email=? OR phone=?", 
                      (ident, data.identifier.strip()))
            user = c.fetchone()
            
            if not user:
                # Auto register on first login attempt if missing
                hashed = hash_password(data.password)
                c.execute("INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
                          (ident, data.identifier.strip(), hashed))
                conn.commit()
                return {
                    "token": "authenticated_user",
                    "email": ident,
                    "phone": data.identifier.strip(),
                    "user_id": f"NL-{c.lastrowid:04d}"
                }

            if user[3] != hash_password(data.password):
                raise HTTPException(status_code=400, detail="Galat Password! Kripya sahi password dalein.")
            
            return {
                "token": "authenticated_user",
                "email": user[1],
                "phone": user[2],
                "user_id": f"NL-{user[0]:04d}"
            }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login Error: {str(e)}")

@app.post("/api/support")
def support(data: SupportData):
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO support_messages (user_id, email, message) VALUES (?, ?, ?)",
                      (data.user_id, data.email, data.message))
            conn.commit()
            return {"message": "Aapka message admin database me save ho gaya hai!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY Render par configure nahi hai!")

    b64_image = None
    if file and file.filename:
        try:
            raw_bytes = await file.read()
            if len(raw_bytes) > 0:
                pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                pil_img.thumbnail((1000, 1000))
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=75)
                b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            pass

    user_text = prompt.strip() if prompt else "Analyze this chart"
    
    is_stock_query = any(k in user_text.lower() for k in ["nifty", "bank", "buy", "sell", "tp", "sl", "target", "stock", "share", "chart", "call", "put", "level"]) or (b64_image is not None)

    if is_stock_query:
        system_prompt = f"""
        Aap Indian Stock Market (NSE/BSE/Nifty/BankNifty/Stocks) ke Expert Quantitative Analyst hain.
        User Sawal: {user_text}

        Agar chart image di gayi hai, toh Y-axis ke REAL PRICES ko dhyan se padhein. Niche diye format me Hinglish me actionable report dein:
        
        📊 1. MARKET BIAS & TREND:
        - Timeframe & Trend: (Bullish / Bearish / Sideways)
        - Current Market Price (CMP) / Zone

        ⚡ 2. TRADE PREDICTION (Buy vs Sell):
        - 🟢 BUY SETUP: Entry Level, Stop Loss (SL), Target 1 & Target 2
        - 🔴 SELL/PUT SETUP: Breakdown Entry, Stop Loss (SL), Target 1 & Target 2
        - ⚖️ RISK-TO-REWARD: (e.g. 1:2)

        🎯 3. ANALYSIS LOGIC:
        - Key Support & Resistance zones aur trade lene ka karan.
        """
    else:
        system_prompt = f"""
        Aap ek Universal AI Assistant hain (ChatGPT aur Gemini Pro ki tarah).
        User ne pucha hai: "{user_text}"
        
        Iska bilkul accurate, helpful aur detail me Hinglish/Hindi me jawab dein. Har topic ki jankari dein.
        """

    # Multi-model pool to eliminate 503 errors
    models = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-flash-latest"]
    
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        parts = []
        if b64_image:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64_image
                }
            })
        parts.append({"text": system_prompt})
        payload = {"contents": [{"parts": parts}]}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    return {"analysis": text}
        except urllib.error.HTTPError as he:
            time.sleep(1) # Backoff and try next model
            continue
        except Exception:
            continue

    # Fallback smart technical engine if Google has temporary 503 outage
    fallback_response = f"""
    📊 **AI Technical Estimation (Live Fallback):**
    
    🎯 **User Query:** {user_text}
    
    🟢 **BUY SETUP:**
    - Entry: Confirmation green candle closing ke baad entry karein.
    - Stop Loss (SL): Pichle swing low ke 0.5% niche strict SL rakhein.
    - Target 1 & 2: 1:1.5 aur 1:2 Risk-Reward ratio.
    
    🔴 **SELL / PUT SETUP:**
    - Entry: Support line breakdown aur retest par enter karein.
    - Stop Loss (SL): Breakdown candle ke high par rakhein.
    - Target: Next major demand zone.
    
    ⚠️ *Note: Google Gemini servers are heavily loaded right now. Strict stop-loss follow karein.*
    """
    return {"analysis": fallback_response}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens AI Pro - Universal Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-[#050811] text-slate-100 min-h-screen font-sans relative pb-28">
        
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div class="fixed bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <!-- SIDEBAR DRAWER (3 LINES) -->
        <div id="drawerOverlay" onclick="toggleMenu()" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 hidden transition-opacity"></div>
        <div id="sidebarDrawer" class="fixed top-0 left-0 h-full w-72 bg-slate-900/95 border-r border-slate-800 p-5 z-50 transform -translate-x-full transition-transform duration-300 flex flex-col justify-between shadow-2xl backdrop-blur-md">
            <div>
                <div class="flex justify-between items-center pb-4 border-b border-slate-800">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid fa-user-astronaut text-emerald-400 text-xl"></i>
                        <span class="font-bold text-lg text-white">Profile & Settings</span>
                    </div>
                    <button onclick="toggleMenu()" class="text-slate-400 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
                </div>

                <div class="mt-6 space-y-3">
                    <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 shadow-inner">
                        <p class="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">User ID</p>
                        <p id="dUserId" class="text-sm font-mono font-bold text-emerald-400 mt-0.5">NL-PRO-01</p>
                    </div>
                    <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 shadow-inner">
                        <p class="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Email</p>
                        <p id="dEmail" class="text-xs text-slate-200 truncate mt-0.5">sinu11915@gmail.com</p>
                    </div>
                    <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 shadow-inner">
                        <p class="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Mobile</p>
                        <p id="dPhone" class="text-xs text-slate-200 mt-0.5">6290565859</p>
                    </div>

                    <button onclick="openSupportModal()" class="w-full mt-4 flex items-center space-x-3 p-3.5 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 hover:from-emerald-500/30 rounded-xl border border-emerald-500/30 text-emerald-300 font-semibold text-xs transition">
                        <i class="fa-solid fa-headset text-base"></i>
                        <span>Customer Support Chat</span>
                    </button>
                </div>
            </div>

            <button onclick="logout()" class="w-full flex items-center justify-center space-x-2 p-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl text-xs font-bold transition">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
                <span>Logout</span>
            </button>
        </div>

        <!-- SUPPORT MODAL -->
        <div id="supportModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-sm p-5 shadow-2xl relative">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="font-bold text-white text-sm flex items-center">
                        <i class="fa-solid fa-headset text-emerald-400 mr-2"></i> Customer Support
                    </h3>
                    <button onclick="closeSupportModal()" class="text-slate-400 text-sm"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-[11px] text-slate-400 mb-3">Admin database me direct save hoga:</p>
                <textarea id="supMsg" rows="3" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-emerald-400" placeholder="Apna sawal likhein..."></textarea>
                <button onclick="sendSupportMessage()" class="w-full mt-3 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-2.5 rounded-xl text-xs transition">Message Bhejein</button>
            </div>
        </div>

        <div class="max-w-md mx-auto p-4 flex flex-col justify-between relative z-10">
            
            <!-- TOP BAR -->
            <div class="flex justify-between items-center py-3 border-b border-slate-800/80">
                <div class="flex items-center space-x-3">
                    <button id="menuBtn" onclick="toggleMenu()" class="hidden text-slate-300 hover:text-emerald-400 text-lg p-2 rounded-xl bg-slate-900/80 border border-slate-800">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid fa-wand-magic-sparkles text-emerald-400 text-2xl drop-shadow-[0_0_10px_rgba(52,211,153,0.7)]"></i>
                        <h1 class="text-xl font-extrabold tracking-wide bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">NiftyLens Pro</h1>
                    </div>
                </div>
                <button id="clearBtn" onclick="clearEverything()" class="hidden text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 px-3 py-1.5 rounded-xl border border-slate-800">
                    <i class="fa-solid fa-rotate-right mr-1"></i> New Chat
                </button>
            </div>

            <!-- EDUCATIONAL WARNING NOTICE -->
            <div class="my-2.5 p-3 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2.5">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-sm mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Yeh tool sirf <u>Educational & Technical Study</u> ke liye hai. Share market me koi guaranteed profit nahi hota. Kripya lalach me aakar bina soche samjhe paisa na lagayein.
                </p>
            </div>

            <!-- AUTH SCREEN -->
            <div id="authSection" class="my-auto py-6">
                <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800 shadow-[0_0_35px_rgba(0,0,0,0.6)] backdrop-blur-xl">
                    <div class="flex justify-center space-x-6 mb-6 border-b border-slate-800 pb-2">
                        <button id="tabL" onclick="switchTab('login')" class="text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1 text-sm">Login</button>
                        <button id="tabR" onclick="switchTab('reg')" class="text-slate-400 font-semibold pb-1 text-sm">Register</button>
                    </div>

                    <div id="loginForm" class="space-y-4">
                        <div>
                            <label class="text-[11px] text-slate-400">Email ya Mobile</label>
                            <input id="lId" type="text" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" value="sinu11915@gmail.com">
                        </div>
                        <div>
                            <label class="text-[11px] text-slate-400">Password</label>
                            <input id="lPass" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="••••••••">
                        </div>
                        <button id="lBtn" onclick="loginUser()" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:opacity-90 text-slate-950 font-black py-3.5 rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] transition text-xs uppercase tracking-wider">Direct Login</button>
                    </div>

                    <div id="regForm" class="space-y-4 hidden">
                        <div>
                            <label class="text-[11px] text-slate-400">Email</label>
                            <input id="rEmail" type="email" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="user@gmail.com">
                        </div>
                        <div>
                            <label class="text-[11px] text-slate-400">Mobile Number</label>
                            <input id="rPhone" type="tel" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="9876543210">
                        </div>
                        <div>
                            <label class="text-[11px] text-slate-400">Password Banayein</label>
                            <input id="rPass" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-xs text-white focus:border-emerald-500 focus:outline-none" placeholder="••••••••">
                        </div>
                        <button id="rBtn" onclick="registerUser()" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:opacity-90 text-slate-950 font-black py-3.5 rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] transition text-xs uppercase tracking-wider">Register Karein</button>
                    </div>
                </div>
            </div>

            <!-- DASHBOARD SCREEN (ASSISTANT & PREDICTION CHAT VIEW) -->
            <div id="dashSection" class="hidden flex-1 py-2 flex flex-col space-y-3">
                
                <!-- ATTACHED IMAGE THUMBNAIL -->
                <div id="attachedPreviewBox" class="hidden relative inline-block max-w-[180px] bg-slate-900 border border-emerald-500/40 rounded-2xl p-1 shadow-xl">
                    <img id="attachedThumb" class="max-h-24 rounded-xl object-contain mx-auto" />
                    <button onclick="removeAttachedImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shadow-lg">✕</button>
                </div>

                <!-- PREDICTION / AI ANSWER DISPLAY -->
                <div id="resBox" class="hidden bg-slate-900/95 border border-emerald-500/40 rounded-3xl p-5 shadow-[0_0_30px_rgba(16,185,129,0.15)]">
                    <h3 class="text-xs font-black text-emerald-400 border-b border-slate-800 pb-2.5 flex items-center tracking-wide">
                        <i class="fa-solid fa-sparkles mr-2 text-cyan-400"></i> AI Response & Analysis
                    </h3>
                    <div id="resText" class="mt-3.5 text-xs leading-relaxed text-slate-200 whitespace-pre-wrap font-sans"></div>
                </div>

                <!-- WELCOME HINT -->
                <div id="welcomeHint" class="p-8 text-center text-slate-500 my-auto">
                    <i class="fa-solid fa-microchip text-4xl mb-3 text-slate-700"></i>
                    <p class="text-xs text-slate-300 font-semibold mb-1">Universal AI + Stock Market Analyst</p>
                    <p class="text-[11px] text-slate-500 leading-relaxed">
                        Niche <strong>+</strong> icon se chart ka screenshot attach karein, ya bina photo ke seedha stock ka naam likhein (e.g. <em>"Bank Nifty buy ya sell"</em>).
                    </p>
                </div>

            </div>

        </div>

        <!-- MODERN BOTTOM CHATGPT STYLE INPUT BAR -->
        <div id="bottomBar" class="hidden fixed bottom-0 left-0 right-0 max-w-md mx-auto p-3.5 bg-slate-950/90 backdrop-blur-2xl border-t border-slate-800/80 z-30">
            <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="previewImg(event)">
            
            <div class="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-1.5 px-3 shadow-2xl focus-within:border-emerald-500 transition">
                <!-- + BUTTON (FOR GALLERY / SCREENSHOT) -->
                <button onclick="document.getElementById('fileInput').click()" class="text-slate-400 hover:text-emerald-400 p-2 text-lg rounded-xl transition" title="Attach Screenshot / Photo">
                    <i class="fa-solid fa-plus-circle text-xl"></i>
                </button>

                <!-- TEXT INPUT (DUNIYA KA KOI BHI PROMPT) -->
                <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Bank Nifty, Tata Steel, ya koi bhi sawal puchiye...">

                <!-- SEND BUTTON -->
                <button id="anBtn" onclick="analyzeChart()" class="bg-gradient-to-r from-emerald-500 to-teal-500 hover:opacity-95 text-slate-950 font-bold p-2.5 px-3.5 rounded-xl text-xs flex items-center justify-center transition shadow-lg">
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
            </div>
        </div>

        <script>
            function resetButtonUI(){
                const btn = document.getElementById('anBtn');
                btn.disabled = false;
                btn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;
            }

            function toggleMenu(){
                const drawer = document.getElementById('sidebarDrawer');
                const overlay = document.getElementById('drawerOverlay');
                if(drawer.classList.contains('-translate-x-full')){
                    drawer.classList.remove('-translate-x-full');
                    overlay.classList.remove('hidden');
                } else {
                    drawer.classList.add('-translate-x-full');
                    overlay.classList.add('hidden');
                }
            }

            function openSupportModal(){
                toggleMenu();
                document.getElementById('supportModal').classList.remove('hidden');
            }
            function closeSupportModal(){
                document.getElementById('supportModal').classList.add('hidden');
            }

            async function sendSupportMessage(){
                const msg = document.getElementById('supMsg').value.trim();
                if(!msg) return alert("Message likhein!");
                const uid = localStorage.getItem('u_id') || 'NL-PRO-01';
                const email = localStorage.getItem('u_email') || 'sinu11915@gmail.com';

                try {
                    const res = await fetch('/api/support', {
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({user_id: uid, email: email, message: msg})
                    });
                    const d = await res.json();
                    alert(d.message);
                    document.getElementById('supMsg').value = '';
                    closeSupportModal();
                } catch(e){ alert("Error: "+e.message); }
            }

            function switchTab(t) {
                if(t==='login'){
                    document.getElementById('loginForm').classList.remove('hidden');
                    document.getElementById('regForm').classList.add('hidden');
                    document.getElementById('tabL').className = "text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1 text-sm";
                    document.getElementById('tabR').className = "text-slate-400 font-semibold pb-1 text-sm";
                } else {
                    document.getElementById('loginForm').classList.add('hidden');
                    document.getElementById('regForm').classList.remove('hidden');
                    document.getElementById('tabR').className = "text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1 text-sm";
                    document.getElementById('tabL').className = "text-slate-400 font-semibold pb-1 text-sm";
                }
            }

            async function registerUser(){
                const email = document.getElementById('rEmail').value;
                const phone = document.getElementById('rPhone').value;
                const password = document.getElementById('rPass').value;
                if(!email || !phone || !password) return alert("Sabhi details bharein!");

                const btn = document.getElementById('rBtn');
                btn.innerText = "Registering...";
                btn.disabled = true;

                try {
                    const res = await fetch('/api/register', {
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({email, phone, password})
                    });
                    const d = await res.json();
                    alert(d.message || "Registration Successful!");
                    switchTab('login');
                } catch(e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.innerText = "Register Karein";
                    btn.disabled = false;
                }
            }

            async function loginUser(){
                const identifier = document.getElementById('lId').value;
                const password = document.getElementById('lPass').value;
                if(!identifier || !password) return alert("Email/Phone aur Password bharein!");

                const btn = document.getElementById('lBtn');
                btn.innerText = "Logging in...";
                btn.disabled = true;

                try {
                    const res = await fetch('/api/login', {
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({identifier, password})
                    });
                    const d = await res.json();
                    if(res.ok){
                        localStorage.setItem('t', d.token);
                        localStorage.setItem('u_id', d.user_id);
                        localStorage.setItem('u_email', d.email);
                        localStorage.setItem('u_phone', d.phone);
                        checkState();
                    } else {
                        alert(d.detail || "Login fail hua!");
                    }
                } catch(e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.innerText = "Direct Login";
                    btn.disabled = false;
                }
            }

            function checkState(){
                if(localStorage.getItem('t')){
                    document.getElementById('authSection').classList.add('hidden');
                    document.getElementById('dashSection').classList.remove('hidden');
                    document.getElementById('bottomBar').classList.remove('hidden');
                    document.getElementById('menuBtn').classList.remove('hidden');
                    document.getElementById('clearBtn').classList.remove('hidden');

                    document.getElementById('dUserId').innerText = localStorage.getItem('u_id') || 'NL-PRO-01';
                    document.getElementById('dEmail').innerText = localStorage.getItem('u_email') || 'sinu11915@gmail.com';
                    document.getElementById('dPhone').innerText = localStorage.getItem('u_phone') || '6290565859';
                } else {
                    document.getElementById('authSection').classList.remove('hidden');
                    document.getElementById('dashSection').classList.add('hidden');
                    document.getElementById('bottomBar').classList.add('hidden');
                    document.getElementById('menuBtn').classList.add('hidden');
                    document.getElementById('clearBtn').classList.add('hidden');
                }
                resetButtonUI();
            }

            function logout(){ 
                localStorage.clear(); 
                toggleMenu();
                checkState(); 
            }

            function previewImg(e){
                const file = e.target.files[0];
                if(file){
                    const r = new FileReader();
                    r.onload = function(ev){
                        document.getElementById('attachedThumb').src = ev.target.result;
                        document.getElementById('attachedPreviewBox').classList.remove('hidden');
                    }
                    r.readAsDataURL(file);
                }
            }

            function removeAttachedImage(){
                document.getElementById('fileInput').value = '';
                document.getElementById('attachedThumb').src = '';
                document.getElementById('attachedPreviewBox').classList.add('hidden');
            }

            function clearEverything(){
                removeAttachedImage();
                document.getElementById('promptInput').value = '';
                document.getElementById('resBox').classList.add('hidden');
                document.getElementById('resText').innerText = '';
                document.getElementById('welcomeHint').classList.remove('hidden');
                resetButtonUI();
            }

            async function analyzeChart(){
                const fi = document.getElementById('fileInput');
                const prompt = document.getElementById('promptInput').value.trim();
                
                if(!prompt && !fi.files[0]){
                    return alert("Kripya kuch likhein (jaise: 'Tata Steel buy ya sell') ya + icon se photo select karein!");
                }

                const btn = document.getElementById('anBtn');
                btn.disabled = true;
                btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

                const fd = new FormData();
                fd.append('prompt', prompt ? prompt : 'Is chart ka analysis karke exact Buy ya Sell levels aur TP SL batao');
                if(fi.files[0]){
                    fd.append('file', fi.files[0]);
                }

                try {
                    const res = await fetch('/api/analyze', { method:'POST', body: fd });
                    const d = await res.json();
                    resetButtonUI();
                    if(res.ok){
                        document.getElementById('welcomeHint').classList.add('hidden');
                        document.getElementById('resBox').classList.remove('hidden');
                        document.getElementById('resText').innerText = d.analysis;
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } else {
                        alert(d.detail || "Error aaya!");
                    }
                } catch(e){ 
                    resetButtonUI();
                    alert("Error: "+e.message); 
                }
            }

            checkState();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
