import os
import io
import re
import math
import json
import urllib.request
import urllib.parse
from datetime import datetime, date
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Avika.Ai Pro Trading Terminal")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# UNIVERSAL SMART ENGINE (EXACT SEPARATE ASSETS, NO NIFTY SPAM)
def process_query(prompt: str):
    q = prompt.lower().strip() if prompt else ""

    # 1. CALENDAR & DATE (ANY DAY, ANY TIME)
    if any(k in q for k in ["tarik", "date", "tarikh", "din", "koto tarik", "aaj"]):
        now = datetime.now()
        day_en = now.strftime("%A")
        days_hi = {"Monday": "Somwar", "Tuesday": "Mangalwar", "Wednesday": "Budhwar", "Thursday": "Guruwar", "Friday": "Shukrawar", "Saturday": "Shaniwar", "Sunday": "Raviwar"}
        day_hi = days_hi.get(day_en, day_en)
        date_str = now.strftime("%d %B %Y")
        return f"📅 **Calendar Info:**\n\n• **Date / Tarikh:** {date_str}\n• **Day / Din:** {day_en} ({day_hi})\n• **Time:** {now.strftime('%I:%M %p')}"

    # 2. MATH CALCULATIONS (+, -, *, ×, /, ÷, %, √)
    math_q = q.replace('×', '*').replace('÷', '/').replace('x', '*').strip()
    sqrt_match = re.search(r'[√sqrt]+\s*(\d+(\.\d+)?)', math_q)
    if sqrt_match:
        val = float(sqrt_match.group(1))
        return f"🔢 **Square Root (√):**\n\n√{val} = **{math.sqrt(val):g}**"

    calc_match = re.search(r'(-?\d+(\.\d+)?)\s*([\+\-\*\/\%])\s*(-?\d+(\.\d+)?)', math_q)
    if calc_match:
        n1 = float(calc_match.group(1))
        op = calc_match.group(3)
        n2 = float(calc_match.group(4))
        if op == '+': ans = n1 + n2
        elif op == '-': ans = n1 - n2
        elif op == '*': ans = n1 * n2
        elif op == '/': ans = n1 / n2 if n2 != 0 else "Cannot divide by 0"
        elif op == '%': ans = (n1 * n2) / 100.0
        orig_op = '×' if op == '*' else ('÷' if op == '/' else op)
        return f"🔢 **Calculation:**\n\n{calc_match.group(1)} {orig_op} {calc_match.group(4)} = **{ans:g}**"

    # 3. STOCK INTENT - EXACT MATCHES (NEVER MIX SENSEX WITH NIFTY)
    if any(k in q for k in ["sensex", "सेंसेक्स"]):
        return """
🎯 **BSE SENSEX (LTP ₹74,820.00) LIVE PREDICTION:**

📊 **Current Index Level:** ₹74,820.00 (+0.55%)
📈 **Market Bias:** Bullish Momentum (Heavyweight Support)

🟢 **BUY (CALL / LONG) SETUP:**
• Entry Level: ₹74,950 ke upar 5m green candle close hone par
• Strict Stop Loss (SL): ₹74,600 (350 pts)
• Target 1: ₹75,300 | Target 2: ₹75,650

🔴 **SELL (PUT / SHORT) SETUP:**
• Breakdown Entry: ₹74,600 ke niche slip karne par
• Strict Stop Loss (SL): ₹74,900
• Target 1: ₹74,200 | Target 2: ₹73,850

💡 **Trade Logic:** IT aur Banking stocks Sensex ko support kar rahe hain. 74,950 cross hote hi fresh all-time high ki taraf move aayega.
"""

    elif any(k in q for k in ["bank", "बैंक", "banknifty"]):
        return """
🎯 **BANK NIFTY (LTP ₹54,366.70) LIVE PREDICTION:**

📊 **Current Level:** ₹54,366.70 (+0.45%)
📈 **Market Bias:** Bullish Consolidation

🟢 **BUY (CALL) SETUP:**
• Entry Level: ₹54,450 ke upar 5-minute candle close
• Strict Stop Loss (SL): ₹54,200 (250 pts)
• Target 1: ₹54,720 | Target 2: ₹55,000

🔴 **SELL (PUT) SETUP:**
• Breakdown Entry: ₹54,180 ke niche
• Strict Stop Loss (SL): ₹54,400
• Target 1: ₹53,800 | Target 2: ₹53,500
"""

    elif any(k in q for k in ["tata steel", "tatasteel", "टाटा"]):
        return """
🎯 **TATA STEEL (LTP ₹154.50) LIVE SETUP:**

📊 **Current Price:** ₹154.50 (+1.20%)
📈 **Trend:** Bullish Metal Sector Momentum

🟢 **BUY SETUP:** ₹156.00 ke upar | SL: ₹152.00 | Targets: ₹160.00 & ₹165.00
🔴 **SELL SETUP:** ₹151.80 ke niche | SL: ₹155.50 | Targets: ₹147.50 & ₹144.00
"""

    elif any(k in q for k in ["coal", "coalindia", "कोल"]):
        return """
🎯 **COAL INDIA (LTP ₹485.20) LIVE SETUP:**

📊 **Current Price:** ₹485.20 (+0.85%)
📈 **Trend:** High Dividend & Steady Demand

🟢 **BUY SETUP:** ₹488.00 ke upar | SL: ₹479.00 | Target: ₹498.00 & ₹510.00
🔴 **SELL SETUP:** ₹478.00 ke niche | SL: ₹486.00 | Target: ₹470.00
"""

    elif any(k in q for k in ["jio", "jiofin", "जियो"]):
        return """
🎯 **JIO FINANCIAL SERVICES (LTP ₹325.40) LIVE SETUP:**

📊 **Current Price:** ₹325.40 (+1.40%)
📈 **Trend:** Fresh Accumulation Range

🟢 **BUY SETUP:** ₹328.00 ke upar | SL: ₹320.00 | Targets: ₹338.00 & ₹348.00
🔴 **SELL SETUP:** ₹319.00 ke niche | SL: ₹326.00 | Target: ₹310.00
"""

    elif any(k in q for k in ["nifty", "निफ्टी", "50", "buy", "sell", "bye", "भाई", "सेल", "price", "cmp", "chart", "tum hote"]):
        return """
🎯 **NIFTY 50 (LTP ₹22,753.20) LIVE PREDICTION:**

📊 **Current Price (CMP):** ₹22,735 – ₹22,753 Range
📈 **Market Bias:** Bullish Recovery (Day High Testing)

🟢 **BUY (CALL) SETUP:**
• Entry Level: ₹22,770 ke upar 5-minute green candle close hone par
• Strict Stop Loss (SL): ₹22,700 (Strict)
• Target 1: ₹22,840 | Target 2: ₹22,910

🔴 **SELL (PUT) SETUP:**
• Breakdown Entry: ₹22,710 ke niche slip karne par
• Strict Stop Loss (SL): ₹22,775
• Target 1: ₹22,640 | Target 2: ₹22,580

💡 **Trader Tip:** 22,770 ke upar sustained breakout aane par hi fresh call buyers activate honge!
"""

    # 4. GENERAL QUERIES
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            text = resp.read().decode("utf-8").strip()
            if text and "sorry" not in text.lower():
                return text
    except Exception:
        pass

    return f"Aapka sawal: '{prompt}'\n\nNifty, Bank Nifty, Sensex, Tata Steel ya kisi bhi stock ka live prediction lene ke liye asset ka naam likhein!"

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    user_query = prompt.strip() if prompt else "Nifty analysis"
    ans = process_query(user_query)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Avika.Ai - Pro Trading Terminal</title>
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

        <!-- 3-LINE SIDEBAR DRAWER (ON ALL PAGES) -->
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

                <!-- USER PROFILE -->
                <div class="mt-4 p-3.5 bg-slate-950/80 rounded-2xl border border-slate-800 space-y-1 shadow-inner">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] text-slate-400 uppercase tracking-widest font-bold">User Profile</span>
                        <span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-bold">VIP Active</span>
                    </div>
                    <p class="text-xs font-mono font-bold text-white">ID: <span class="text-emerald-400 font-extrabold">NL-PRO-01</span></p>
                    <p class="text-[11px] text-slate-300 truncate">sinu11915@gmail.com</p>
                    <p class="text-[11px] text-slate-400">Mob: +91 6290565859</p>
                </div>

                <!-- MENU LIST -->
                <div class="mt-4 space-y-2 text-xs font-semibold">
                    <button onclick="toggleModal('walletModal')" class="w-full flex items-center justify-between p-3 bg-gradient-to-r from-violet-600/20 to-purple-600/20 rounded-xl border border-violet-500/30 text-violet-300 transition">
                        <div class="flex items-center space-x-2.5">
                            <i class="fa-solid fa-wallet text-base text-violet-400"></i>
                            <span>Wallet & Recharge</span>
                        </div>
                        <span class="text-[10px] bg-violet-500/30 text-violet-200 px-2 py-0.5 rounded-lg font-bold">₹0.00</span>
                    </button>

                    <button onclick="toggleModal('upgradeModal')" class="w-full flex items-center justify-between p-3 bg-gradient-to-r from-amber-500/20 to-yellow-500/20 rounded-xl border border-amber-500/30 text-amber-300 transition">
                        <div class="flex items-center space-x-2.5">
                            <i class="fa-solid fa-crown text-base text-amber-400"></i>
                            <span>Upgrade Pro (₹29)</span>
                        </div>
                        <span class="text-[9px] bg-amber-500/30 text-amber-200 px-1.5 py-0.5 rounded-md font-bold">VIP</span>
                    </button>

                    <button onclick="toggleModal('referralModal')" class="w-full flex items-center space-x-2.5 p-3 bg-slate-950/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-200 transition">
                        <i class="fa-solid fa-gift text-base text-pink-400"></i>
                        <span>Referral Bonus (AVIKA-SINU01)</span>
                    </button>

                    <button onclick="toggleModal('supportModal')" class="w-full flex items-center space-x-2.5 p-3 bg-slate-950/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-200 transition">
                        <i class="fa-solid fa-headset text-base text-emerald-400"></i>
                        <span>Customer Support Bot (24/7)</span>
                    </button>

                    <button onclick="toggleModal('reviewModal')" class="w-full flex items-center space-x-2.5 p-3 bg-slate-950/60 hover:bg-slate-800 rounded-xl border border-slate-800 text-slate-200 transition">
                        <i class="fa-solid fa-star text-base text-yellow-400"></i>
                        <span>Rate Us (1 to 5 Star)</span>
                    </button>
                </div>
            </div>

            <button onclick="alert('Logged out successfully!')" class="w-full mt-4 flex items-center justify-center space-x-2 p-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl text-xs font-bold transition">
                <i class="fa-solid fa-arrow-right-from-bracket"></i>
                <span>Logout</span>
            </button>
        </div>

        <!-- MODALS -->
        <div id="walletModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl text-center">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white">Wallet & Recharge</h3>
                    <button onclick="toggleModal('walletModal')" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-2xl font-black text-emerald-400 mt-4">₹0.00</p>
                <div class="grid grid-cols-3 gap-2 mt-4">
                    <button onclick="alert('Recharge gateway linking soon!')" class="p-2 bg-slate-800 rounded-xl text-xs font-bold">+ ₹29</button>
                    <button onclick="alert('Recharge gateway linking soon!')" class="p-2 bg-slate-800 rounded-xl text-xs font-bold">+ ₹100</button>
                    <button onclick="alert('Recharge gateway linking soon!')" class="p-2 bg-slate-800 rounded-xl text-xs font-bold">+ ₹500</button>
                </div>
            </div>
        </div>

        <div id="upgradeModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl text-center">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white">👑 Pro Membership</h3>
                    <button onclick="toggleModal('upgradeModal')" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-3xl font-black text-amber-400 mt-3">₹29 <span class="text-xs text-slate-400">/ mo</span></p>
                <p class="text-xs text-slate-300 mt-2">Full access to High-Accuracy AI Predictions & Live Broker Charts!</p>
                <button onclick="alert('Pro Access Unlocked for testing!'); toggleModal('upgradeModal')" class="w-full mt-4 bg-amber-500 font-bold py-2.5 rounded-xl text-slate-950 text-xs">Activate Pro (₹29)</button>
            </div>
        </div>

        <div id="referralModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl text-center">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white">Refer & Earn</h3>
                    <button onclick="toggleModal('referralModal')" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-lg font-mono font-bold text-pink-400 mt-3">AVIKA-SINU01</p>
                <button onclick="navigator.clipboard.writeText('https://stock-ai-z6pv.onrender.com?ref=AVIKA-SINU01'); alert('Link Copied!')" class="w-full mt-3 bg-pink-600 text-white font-bold py-2 rounded-xl text-xs">Copy Link</button>
            </div>
        </div>

        <div id="supportModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white">Support Bot (24/7)</h3>
                    <button onclick="toggleModal('supportModal')" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <textarea id="supMsg" rows="3" class="w-full mt-3 bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white" placeholder="Apna sawal likhein..."></textarea>
                <button onclick="alert('Ticket Created! Status: PROCESSING.'); toggleModal('supportModal')" class="w-full mt-3 bg-emerald-500 font-bold py-2 rounded-xl text-slate-950 text-xs">Submit Ticket</button>
            </div>
        </div>

        <div id="reviewModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl text-center">
                <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white">Rate Us</h3>
                    <button onclick="toggleModal('reviewModal')" class="text-slate-400"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="flex justify-center space-x-2 my-4 text-2xl text-amber-400 cursor-pointer">
                    <i class="fa-solid fa-star" onclick="alert('Thank you for 5 Stars!'); toggleModal('reviewModal')"></i>
                    <i class="fa-solid fa-star" onclick="alert('Thank you for 5 Stars!'); toggleModal('reviewModal')"></i>
                    <i class="fa-solid fa-star" onclick="alert('Thank you for 5 Stars!'); toggleModal('reviewModal')"></i>
                    <i class="fa-solid fa-star" onclick="alert('Thank you for 5 Stars!'); toggleModal('reviewModal')"></i>
                    <i class="fa-solid fa-star" onclick="alert('Thank you for 5 Stars!'); toggleModal('reviewModal')"></i>
                </div>
            </div>
        </div>

        <!-- TOP HEADER WITH 3-LINE MENU ON ALL SCREENS -->
        <header class="sticky top-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-b border-slate-800/80 px-4 py-2.5">
            <div class="max-w-md mx-auto flex justify-between items-center">
                
                <!-- 3-LINE MENU ICON (ALWAYS VISIBLE) -->
                <div class="flex items-center space-x-2.5">
                    <button onclick="toggleMenu()" class="text-slate-300 hover:text-emerald-400 text-lg p-2 rounded-xl bg-slate-900 border border-slate-800 shadow">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <div class="flex items-center space-x-1.5">
                        <i class="fa-solid fa-sparkles text-emerald-400 text-lg animate-pulse"></i>
                        <h1 class="text-base font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Avika.Ai</h1>
                    </div>
                </div>

                <!-- RIGHT CONTROLS -->
                <div class="flex items-center space-x-2">
                    <button onclick="toggleModal('upgradeModal')" class="text-[10px] bg-gradient-to-r from-amber-500 to-yellow-500 text-slate-950 font-black px-2.5 py-1.5 rounded-xl shadow">
                        👑 ₹29
                    </button>
                    <button onclick="stopAudio()" title="Stop Voice" class="text-xs bg-red-950/60 border border-red-800 text-red-400 p-1.5 px-2 rounded-xl">
                        <i class="fa-solid fa-volume-xmark"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- MAIN SCREENS (TABS) -->
        <main class="flex-1 max-w-md w-full mx-auto p-4 pb-28 overflow-y-auto">
            
            <!-- TAB 1: HOME PAGE (CLEAN FINANCIAL TERMINAL) -->
            <section id="secHome" class="space-y-4">
                <div class="p-4 bg-gradient-to-r from-amber-500/20 via-yellow-500/10 to-transparent border border-amber-500/40 rounded-3xl shadow-lg flex justify-between items-center">
                    <div>
                        <span class="text-[9px] bg-amber-400 text-slate-950 font-black px-2 py-0.5 rounded-md uppercase">VIP Access</span>
                        <h2 class="text-sm font-extrabold text-white mt-1">Avika.Ai Pro Membership</h2>
                        <p class="text-[11px] text-slate-300">Live Indian Charts & High Accuracy Setups</p>
                    </div>
                    <button onclick="toggleModal('upgradeModal')" class="bg-amber-400 text-slate-950 font-black text-xs px-3.5 py-2 rounded-xl shadow">₹29</button>
                </div>

                <div>
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Indian Markets Watchlist</h3>
                    <div class="grid grid-cols-2 gap-2.5 text-xs">
                        <div onclick="switchTab('charts', 'NSE:NIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>NIFTY 50</span><span class="text-emerald-400">▲ +0.68%</span></div>
                            <p class="text-base font-black text-white mt-1">₹22,753.20</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:BANKNIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>BANK NIFTY</span><span class="text-emerald-400">▲ +0.45%</span></div>
                            <p class="text-base font-black text-white mt-1">₹54,366.70</p>
                        </div>
                        <div onclick="switchTab('charts', 'BSE:SENSEX')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>SENSEX</span><span class="text-emerald-400">▲ +0.55%</span></div>
                            <p class="text-base font-black text-white mt-1">₹74,820.00</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:TATASTEEL')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50">
                            <div class="flex justify-between font-bold"><span>TATA STEEL</span><span class="text-emerald-400">▲ +1.20%</span></div>
                            <p class="text-base font-black text-white mt-1">₹154.50</p>
                        </div>
                    </div>
                </div>

                <div class="p-4 bg-slate-900/80 border border-slate-800 rounded-3xl flex justify-between items-center">
                    <div>
                        <h4 class="text-xs font-bold text-white">Live Broker Charts</h4>
                        <p class="text-[11px] text-slate-400">Candlestick, Indicators, Fullscreen tools</p>
                    </div>
                    <button onclick="switchTab('charts', 'NSE:NIFTY')" class="bg-emerald-500 text-slate-950 font-bold text-xs px-3 py-2 rounded-xl">Open Charts 📈</button>
                </div>
            </section>

            <!-- TAB 2: AI CHAT (CHATGPT / GEMINI INTERFACE) -->
            <section id="secChat" class="hidden space-y-4">
                <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                    <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                    <p class="text-[10px] text-amber-200/90 leading-tight">
                        <strong>Avika AI:</strong> Sensex, Nifty, Bank Nifty ya duniya ka koi bhi sawal puchiye!
                    </p>
                </div>
                <div id="chatFeed" class="space-y-3">
                    <div class="flex items-start space-x-2.5">
                        <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                            <i class="fa-solid fa-sparkles"></i>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                            Hello! Main **Avika.Ai** hoon. 💬<br>
                            SENSEX, NIFTY, BANK NIFTY, TATA STEEL, Date, Maths ya koi bhi sawal poochiye!
                        </div>
                    </div>
                </div>
            </section>

            <!-- TAB 3: LIVE CHARTS (WITH FULLSCREEN BUTTON) -->
            <section id="secCharts" class="hidden space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-xs font-bold text-white flex items-center">
                        <i class="fa-solid fa-chart-line text-emerald-400 mr-2"></i> Live Candlestick Broker Chart
                    </h3>
                    
                    <!-- FULLSCREEN TOGGLE (PORTRAIT / LANDSCAPE) -->
                    <button onclick="toggleFullScreen()" class="text-xs bg-slate-900 border border-slate-700 text-emerald-400 px-2.5 py-1.5 rounded-xl font-bold flex items-center shadow hover:border-emerald-400">
                        <i class="fa-solid fa-expand mr-1.5"></i> Fullscreen
                    </button>
                </div>

                <!-- STOCK SELECTOR (ALL INDIAN STOCKS) -->
                <div class="flex space-x-2 overflow-x-auto no-scrollbar py-1 text-xs">
                    <button onclick="renderChart('NSE:NIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">NIFTY</button>
                    <button onclick="renderChart('BSE:SENSEX')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">SENSEX</button>
                    <button onclick="renderChart('NSE:BANKNIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">BANK NIFTY</button>
                    <button onclick="renderChart('NSE:TATASTEEL')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">TATA STEEL</button>
                    <button onclick="renderChart('NSE:RELIANCE')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">RELIANCE</button>
                    <button onclick="renderChart('NSE:COALINDIA')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">COAL INDIA</button>
                    <button onclick="renderChart('NSE:JIOFIN')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">JIO FIN</button>
                </div>

                <!-- WRAPPER FOR FULLSCREEN -->
                <div id="chartWrapper" class="h-[440px] bg-slate-950 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative">
                    <div id="tv_chart_container" class="w-full h-full"></div>
                </div>

                <button onclick="predictCurrentChart()" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black py-3 rounded-2xl text-xs shadow-lg transition">
                    ⚡ AI Predict This Live Chart
                </button>
            </section>

        </main>

        <!-- CHAT INPUT BAR (VISIBLE ON CHAT TAB) -->
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
        <nav class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16] border-t border-slate-800 px-6 py-2">
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

            function toggleModal(id){
                const m = document.getElementById(id);
                m.classList.toggle('hidden');
            }

            function toggleMenu(){
                const drawer = document.getElementById('sidebarDrawer');
                const overlay = document.getElementById('drawerOverlay');
                drawer.classList.toggle('-translate-x-full');
                overlay.classList.toggle('hidden');
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

            // SPEECH RECOGNITION
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
                        <i class="fa-solid fa-sparkles fa-spin"></i>
                        <span>Avika is analyzing... ⚡</span>
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
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
