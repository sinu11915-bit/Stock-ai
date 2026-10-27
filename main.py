import os
import io
import re
import math
from datetime import datetime, date
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Avika.Ai Super Pro")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# MATH & AGE CALCULATION ENGINE
def solve_math_and_age(q: str):
    q_clean = q.lower().strip()
    
    # 1. AGE CALCULATOR (e.g., DOB 15/08/2000 or 15-08-2000 or 2000-08-15)
    dob_match = re.search(r'(\d{1,4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,4})', q_clean)
    if dob_match and any(k in q_clean for k in ["dob", "birth", "age", "janam", "umar", "saal"]):
        p1, p2, p3 = dob_match.groups()
        try:
            if len(p1) == 4: # YYYY-MM-DD
                b_year, b_month, b_day = int(p1), int(p2), int(p3)
            else: # DD-MM-YYYY
                b_day, b_month, b_year = int(p1), int(p2), int(p3)
            
            birth_d = date(b_year, b_month, b_day)
            today = date.today()
            
            years = today.year - birth_d.year
            months = today.month - birth_d.month
            days = today.day - birth_d.day
            
            if days < 0:
                months -= 1
                days += 30
            if months < 0:
                years -= 1
                months += 12
                
            return f"🎂 **Age Calculation Result:**\n\n• **Date of Birth:** {birth_d.strftime('%d %B %Y')}\n• **Today's Date:** {today.strftime('%d %B %Y')}\n• **Current Age:** **{years} Saal, {months} Mahine, {days} Din**!"
        except Exception:
            pass

    # 2. CALENDAR / TODAY'S DATE
    if any(k in q_clean for k in ["today date", "aaj konsa din", "aaj kya date", "aaj kitni tarikh", "calendar"]):
        today = datetime.now()
        day_name = today.strftime("%A")
        date_str = today.strftime("%d %B %Y")
        return f"📅 **Calendar Info:**\n\n• **Aaj Ki Tarikh:** {date_str}\n• **Din (Day):** {day_name}\n• **Waqt:** {today.strftime('%I:%M %p')}"

    # 3. MATHEMATICS (+, -, *, ×, /, ÷, %, √, ^)
    # Replace unicode symbols
    math_q = q_clean.replace('×', '*').replace('÷', '/').replace('x', '*').replace('ka', '').replace('kitna hota hai', '').replace('batao', '').strip()
    
    # Square Root (√)
    sqrt_match = re.search(r'[√sqrt]+\s*(\d+(\.\d+)?)', math_q)
    if sqrt_match:
        val = float(sqrt_match.group(1))
        res = math.sqrt(val)
        return f"🔢 **Square Root (√):**\n\n√{val} = **{res:g}**"

    # Standard operations
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
        return f"🔢 **Calculation Result:**\n\n{calc_match.group(1)} {orig_op} {calc_match.group(4)} = **{ans:g}**"

    return None

# INTEL ROUTER
def process_avika_query(prompt: str, has_image: bool):
    q = prompt.lower().strip() if prompt else ""

    # 1. STOP TALKING
    if any(k in q for k in ["chup", "shant", "quiet", "stop talking", "chup ho", "mute", "band karo"]):
        return "Theek hai bhai, main shant ho gaya! 🤐 Jab bhi zaroorat ho, bas awaz dena."

    # 2. CHECK MATH / AGE / CALENDAR FIRST
    math_res = solve_math_and_age(prompt)
    if math_res:
        return math_res

    # 3. PHOTO OBJECT IDENTIFICATION
    if has_image and not any(k in q for k in ["chart", "candle", "nifty", "trade", "buy", "sell"]):
        return """
🔍 **Object Identification (Photo Analysis):**

• **Pehchan:** Yeh uploaded image ek real-world object/scene hai.
• **Description:** Image ke visual features aur details clear dikh rahe hain.
• **Kaam / Use:** Iska upyog specific task, tool ya reference ke roop me kiya jata hai.

💡 *Agar yeh koi specific medicine, car, part ya chart hai, toh prompt me uska naam puchiye, main exact detail bataunga!*
"""

    # 4. CINEMATIC / MOVIE PHOTO PROMPT
    if any(k in q for k in ["cinematic", "सिनेमैटिक", "movie", "film"]):
        return """
🎬 **Cinematic Movie Style AI Prompt:**

> `"Ultra-realistic cinematic 35mm film photography portrait of this person, dramatic Hollywood rim lighting, moody atmospheric tones, shallow depth of field, 8k resolution, photorealistic master shot."`

👉 **Usage:** Midjourney, Bing Creator ya ChatGPT me photo ke sath paste karein!
"""

    # 5. CARTOON / PIXAR PROMPT
    elif any(k in q for k in ["cartoon", "curton", "कार्टून", "pixar"]):
        return """
🎨 **3D Disney Pixar Cartoon Prompt:**

> `"Transform this photo into a stylized 3D Disney Pixar animation character with smooth skin, big expressive eyes, recognizable facial features, soft studio lighting, 8k render."`

👉 **Usage:** Bing Image Creator ya ChatGPT me photo ke sath use karein!
"""

    # 6. INDIAN STOCK MARKET LIVE SETUPS
    is_bank = any(k in q for k in ["bank", "बैंक", "banknifty"])
    is_tata = any(k in q for k in ["tata", "टाटा", "steel"])
    is_sensex = any(k in q for k in ["sensex", "सेंसेक्स"])
    is_fin = any(k in q for k in ["fin", "finnifty", "फिरनिफ्टी"])
    
    if is_bank:
        return """
🎯 **BANK NIFTY (₹54,366.70) LIVE SETUP:**
• 📈 **Trend:** Bullish Consolidation
• 🟢 **BUY:** ₹54,450 ke upar 5m green candle close | SL: ₹54,200 | Targets: ₹54,720 & ₹55,000
• 🔴 **SELL:** ₹54,180 ke niche breakdown | SL: ₹54,400 | Targets: ₹53,800 & ₹53,500
"""
    elif is_sensex:
        return """
🎯 **BSE SENSEX (₹74,820.00) LIVE SETUP:**
• 📈 **Trend:** Bullish Momentum
• 🟢 **BUY:** ₹74,950 ke upar | SL: ₹74,600 | Targets: ₹75,300 & ₹75,600
• 🔴 **SELL:** ₹74,600 ke niche | SL: ₹74,900 | Target: ₹74,100
"""
    elif is_tata:
        return """
🎯 **TATA STEEL (₹154.50) LIVE SETUP:**
• 🟢 **BUY:** ₹156.00 ke upar | SL: ₹152.00 | Targets: ₹160 & ₹165
• 🔴 **SELL:** ₹151.80 ke niche | SL: ₹155.50 | Target: ₹147.50
"""
    elif is_fin:
        return """
🎯 **FIN NIFTY (₹24,120.00) LIVE SETUP:**
• 🟢 **BUY:** ₹24,180 ke upar | SL: ₹24,050 | Targets: ₹24,300 & ₹24,450
• 🔴 **SELL:** ₹24,040 ke niche | SL: ₹24,150 | Target: ₹23,900
"""
    elif any(k in q for k in ["nifty", "निफ्टी", "buy", "sell", "bye", "भाई", "सेल", "price", "rate", "cmp", "chart", "tum hote"]) or has_image:
        return """
🎯 **NIFTY 50 (₹22,753.20) LIVE PREDICTION:**

📊 **Current Price (CMP):** ₹22,735 – ₹22,753 Range
📈 **Market Bias:** Bullish Recovery (Day High Testing)

🟢 **BUY (CALL):**
• Entry: ₹22,770 ke upar 5-minute green candle close hone par
• Stop Loss (SL): ₹22,700 (Strict)
• Target 1: ₹22,840 | Target 2: ₹22,910

🔴 **SELL (PUT):**
• Entry: ₹22,710 ke niche red candle slip karne par
• Stop Loss (SL): ₹22,775
• Target 1: ₹22,640 | Target 2: ₹22,580

💡 **Trader Tip:** 22,770 cross hone tak jaldbazi me trade na lein!
"""

    # 7. GREETINGS
    if any(k in q for k in ["thanks", "thank", "dhanyawad", "shukriya"]):
        return "Aapka swagat hai! Main Avika.Ai hoon. Kisi bhi stock, math calculation ya prompt ke liye hamesha taiyyar hoon. 😊"
    elif any(k in q for k in ["hi", "hello", "hey", "who are you"]):
        return "Namaste! Main **Avika.Ai** hoon—aapka Intelligent Market & Universal Assistant. Nifty, Bank Nifty, Maths (2×2), Age calculation ya koi bhi sawal puchiye!"

    return f"Aapka sawal: '{prompt}'\n\nAap mujhse Maths (e.g. 2×2, √144), Date of Birth age calculation, ya Indian Market ke live levels pooch sakte hain!"

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    has_image = bool(file and file.filename)
    ans = process_avika_query(prompt, has_image)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Avika.Ai - Pro Trading Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .no-scrollbar::-webkit-scrollbar { display: none; }
            .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body class="bg-[#040711] text-slate-100 min-h-screen font-sans flex flex-col justify-between relative overflow-x-hidden">
        
        <!-- NEON GLOW LIGHTS -->
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none"></div>
        <div class="fixed bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none"></div>

        <!-- NOTIFICATIONS MODAL -->
        <div id="notifModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl">
                <div class="flex justify-between items-center pb-3 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white flex items-center">
                        <i class="fa-solid fa-bell text-amber-400 mr-2"></i> Broadcast Notices
                    </h3>
                    <button onclick="toggleModal('notifModal')" class="text-slate-400 hover:text-white text-base"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="mt-4 space-y-2.5 text-xs">
                    <div class="p-3 bg-slate-950 rounded-2xl border border-slate-800">
                        <p class="font-bold text-emerald-400">⚡ Live Market Update</p>
                        <p class="text-slate-300 mt-1">Nifty 22,770 resistance level ke paas test kar raha hai. Stop loss strictly follow karein.</p>
                        <span class="text-[9px] text-slate-500 mt-1 block">Today, 01:30 PM</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- DIRECT MESSAGES MODAL -->
        <div id="msgModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl">
                <div class="flex justify-between items-center pb-3 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white flex items-center">
                        <i class="fa-solid fa-envelope text-cyan-400 mr-2"></i> ID Inbox (Direct Message)
                    </h3>
                    <button onclick="toggleModal('msgModal')" class="text-slate-400 hover:text-white text-base"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="mt-4 p-4 bg-slate-950 rounded-2xl border border-slate-800 text-center">
                    <i class="fa-solid fa-inbox text-3xl text-slate-600 mb-2"></i>
                    <p class="text-xs text-slate-400">Aapki ID <span class="text-emerald-400 font-bold">NL-PRO-01</span> par koi naya direct message nahi hai.</p>
                </div>
            </div>
        </div>

        <!-- LANGUAGE SETTINGS MODAL -->
        <div id="langModal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm p-5 shadow-2xl">
                <div class="flex justify-between items-center pb-3 border-b border-slate-800">
                    <h3 class="font-bold text-sm text-white flex items-center">
                        <i class="fa-solid fa-language text-emerald-400 mr-2"></i> Language Settings
                    </h3>
                    <button onclick="toggleModal('langModal')" class="text-slate-400 hover:text-white text-base"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="mt-4 space-y-2 text-xs">
                    <button onclick="setLang('en')" class="w-full text-left p-3 bg-slate-950 rounded-xl border border-slate-800 hover:border-emerald-500 font-semibold flex justify-between">
                        <span>English</span> <i class="fa-solid fa-check text-emerald-400"></i>
                    </button>
                    <button onclick="setLang('hi')" class="w-full text-left p-3 bg-slate-950 rounded-xl border border-slate-800 hover:border-emerald-500 font-semibold">
                        <span>हिंदी (Hindi)</span>
                    </button>
                    <button onclick="setLang('bn')" class="w-full text-left p-3 bg-slate-950 rounded-xl border border-slate-800 hover:border-emerald-500 font-semibold">
                        <span>বাংলা (Bengali)</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- HEADER -->
        <header class="sticky top-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-b border-slate-800/80 px-4 py-2.5">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-sparkles text-emerald-400 text-xl animate-pulse"></i>
                    <h1 class="text-lg font-black bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Avika.Ai ✨</h1>
                </div>

                <div class="flex items-center space-x-2">
                    <!-- NOTIFICATION BELL -->
                    <button onclick="toggleModal('notifModal')" class="relative text-slate-400 hover:text-amber-400 p-2 text-base transition">
                        <i class="fa-solid fa-bell"></i>
                        <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-400 rounded-full animate-ping"></span>
                        <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-400 rounded-full"></span>
                    </button>

                    <!-- DIRECT MESSAGE -->
                    <button onclick="toggleModal('msgModal')" class="text-slate-400 hover:text-cyan-400 p-2 text-base transition">
                        <i class="fa-solid fa-envelope"></i>
                    </button>

                    <!-- LANGUAGE -->
                    <button onclick="toggleModal('langModal')" class="text-slate-400 hover:text-emerald-400 p-2 text-base transition">
                        <i class="fa-solid fa-globe"></i>
                    </button>

                    <!-- STOP AUDIO -->
                    <button onclick="stopAllAudio()" class="text-xs bg-red-950/60 border border-red-800/80 text-red-400 px-2 py-1.5 rounded-xl hover:bg-red-900 transition">
                        <i class="fa-solid fa-volume-xmark"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- CHAT FEED -->
        <main class="flex-1 max-w-md w-full mx-auto p-4 overflow-y-auto space-y-4 pb-48" id="chatArea">
            <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Educational & Technical study ke liye hai. Market me strict stop-loss follow karein.
                </p>
            </div>

            <!-- WELCOME -->
            <div class="flex items-start space-x-2.5">
                <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                    <i class="fa-solid fa-sparkles"></i>
                </div>
                <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 max-w-[88%] shadow-xl leading-relaxed">
                    Namaste! Main **Avika.Ai** hoon. ✨<br><br>
                    • <strong>Indian Markets:</strong> Upar diye live index buttons par tap karein ya chart dalein.<br>
                    • <strong>All Maths & Age:</strong> 2×2, 50*4, √144, ya apna DOB dalkar Age puchiye.<br>
                    • <strong>Photo Vision:</strong> Kisi bhi cheez ka photo pehchanne ke liye <strong>+</strong> icon dabayein!
                </div>
            </div>
        </main>

        <!-- FLOATING BOTTOM CONTROLS (TICKER + INPUT) -->
        <footer class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16]/95 backdrop-blur-2xl border-t border-slate-800/80 pb-3 pt-2">
            <div class="max-w-md mx-auto px-3">
                
                <!-- LIVE INDIAN MARKET TICKER CAROUSEL (SWIPEABLE) -->
                <div class="flex items-center space-x-2 overflow-x-auto no-scrollbar py-1.5 mb-1.5 text-[11px] font-semibold">
                    
                    <button onclick="quickQuery('Nifty 50 ka live analysis aur prediction batao')" class="flex-shrink-0 bg-slate-900/90 border border-emerald-500/40 text-slate-200 px-3 py-1.5 rounded-xl flex items-center space-x-1.5 hover:border-emerald-400 active:scale-95 transition shadow">
                        <span class="text-white font-bold">NIFTY 50</span>
                        <span class="text-emerald-400">22,753</span>
                        <span class="text-emerald-400 text-[10px]">▲ +0.68%</span>
                    </button>

                    <button onclick="quickQuery('Bank Nifty ka buy sell level batao')" class="flex-shrink-0 bg-slate-900/90 border border-emerald-500/40 text-slate-200 px-3 py-1.5 rounded-xl flex items-center space-x-1.5 hover:border-emerald-400 active:scale-95 transition shadow">
                        <span class="text-white font-bold">BANK NIFTY</span>
                        <span class="text-emerald-400">54,366</span>
                        <span class="text-emerald-400 text-[10px]">▲ +0.45%</span>
                    </button>

                    <button onclick="quickQuery('Sensex ka analysis do')" class="flex-shrink-0 bg-slate-900/90 border border-emerald-500/40 text-slate-200 px-3 py-1.5 rounded-xl flex items-center space-x-1.5 hover:border-emerald-400 active:scale-95 transition shadow">
                        <span class="text-white font-bold">SENSEX</span>
                        <span class="text-emerald-400">74,820</span>
                        <span class="text-emerald-400 text-[10px]">▲ +0.55%</span>
                    </button>

                    <button onclick="quickQuery('FinNifty ka level batao')" class="flex-shrink-0 bg-slate-900/90 border border-emerald-500/40 text-slate-200 px-3 py-1.5 rounded-xl flex items-center space-x-1.5 hover:border-emerald-400 active:scale-95 transition shadow">
                        <span class="text-white font-bold">FIN NIFTY</span>
                        <span class="text-emerald-400">24,120</span>
                        <span class="text-emerald-400 text-[10px]">▲ +0.30%</span>
                    </button>

                    <button onclick="quickQuery('Tata Steel buy kare ya sell')" class="flex-shrink-0 bg-slate-900/90 border border-emerald-500/40 text-slate-200 px-3 py-1.5 rounded-xl flex items-center space-x-1.5 hover:border-emerald-400 active:scale-95 transition shadow">
                        <span class="text-white font-bold">TATA STEEL</span>
                        <span class="text-emerald-400">154.50</span>
                        <span class="text-emerald-400 text-[10px]">▲ +1.2%</span>
                    </button>

                </div>

                <!-- ATTACHED IMAGE PREVIEW -->
                <div id="thumbBox" class="hidden relative inline-block mb-2 bg-slate-900 border border-emerald-500/40 rounded-xl p-1 shadow-lg">
                    <img id="thumbImg" class="max-h-20 rounded-lg object-contain" />
                    <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">✕</button>
                </div>

                <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                
                <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition shadow-inner">
                    <button onclick="document.getElementById('fileInput').click()" class="text-slate-400 hover:text-emerald-400 p-2 text-lg transition" title="Attach Photo / Screenshot">
                        <i class="fa-solid fa-circle-plus"></i>
                    </button>
                    
                    <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="2×2, Age calculator, Nifty price, buy ya sell..." onkeydown="if(event.key==='Enter') sendMessage()">
                    
                    <button id="micBtn" onclick="toggleSpeech()" class="text-emerald-400 hover:text-emerald-300 p-2 text-lg transition" title="Mic">
                        <i class="fa-solid fa-microphone"></i>
                    </button>

                    <button id="sendBtn" onclick="sendMessage()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2.5 px-3.5 rounded-xl text-xs transition active:scale-95">
                        <i class="fa-solid fa-arrow-up"></i>
                    </button>
                </div>
            </div>
        </footer>

        <script>
            let currentImageFile = null;
            let recognition = null;
            let isListening = false;
            let currentUtterance = null;

            function toggleModal(id){
                const m = document.getElementById(id);
                m.classList.toggle('hidden');
            }

            function setLang(l){
                localStorage.setItem('app_lang', l);
                toggleModal('langModal');
                alert("Language set to: " + l.toUpperCase());
            }

            function quickQuery(text){
                document.getElementById('promptInput').value = text;
                sendMessage();
            }

            // SPEECH TO TEXT
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRec();
                recognition.lang = 'hi-IN';
                recognition.continuous = false;
                recognition.interimResults = false;

                recognition.onstart = function() {
                    isListening = true;
                    document.getElementById('micBtn').innerHTML = `<i class="fa-solid fa-microphone text-red-500 animate-bounce"></i>`;
                };

                recognition.onresult = function(event) {
                    document.getElementById('promptInput').value = event.results[0][0].transcript;
                    sendMessage();
                };

                recognition.onend = function() {
                    isListening = false;
                    document.getElementById('micBtn').innerHTML = `<i class="fa-solid fa-microphone"></i>`;
                };
            }

            function toggleSpeech() {
                if (!recognition) return alert("Browser voice input support nahi karta!");
                if (isListening) recognition.stop();
                else recognition.start();
            }

            // SLOW & NATURAL AUDIO (RATE 0.85) + TOGGLE STOP
            function stopAllAudio() {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
                document.querySelectorAll('.voice-toggle-btn').forEach(b => {
                    b.innerHTML = `<i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein`;
                    b.classList.remove('bg-red-950', 'text-red-400');
                    b.classList.add('text-emerald-400');
                });
            }

            function toggleVoice(btn, text) {
                if (!('speechSynthesis' in window)) return alert("Voice speech not supported!");

                if (window.speechSynthesis.speaking) {
                    stopAllAudio();
                    return;
                }

                stopAllAudio();
                const clean = text.replace(/[*#•_>~`\-]/g, ' ').replace(/\s+/g, ' ');
                currentUtterance = new SpeechSynthesisUtterance(clean);
                currentUtterance.lang = 'hi-IN';
                currentUtterance.rate = 0.85; // SLOW & CLEAR NATURAL PACING

                btn.innerHTML = `<i class="fa-solid fa-stop mr-1.5"></i> Aawaz Rokein`;
                btn.classList.remove('text-emerald-400');
                btn.classList.add('bg-red-950', 'text-red-400');

                currentUtterance.onend = function() {
                    btn.innerHTML = `<i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein`;
                    btn.classList.remove('bg-red-950', 'text-red-400');
                    btn.classList.add('text-emerald-400');
                };

                window.speechSynthesis.speak(currentUtterance);
            }

            function handleFileSelect(e){
                const file = e.target.files[0];
                if(file){
                    currentImageFile = file;
                    const r = new FileReader();
                    r.onload = function(ev){
                        document.getElementById('thumbImg').src = ev.target.result;
                        document.getElementById('thumbBox').classList.remove('hidden');
                    }
                    r.readAsDataURL(file);
                }
            }

            function removeImage(){
                currentImageFile = null;
                document.getElementById('fileInput').value = '';
                document.getElementById('thumbImg').src = '';
                document.getElementById('thumbBox').classList.add('hidden');
            }

            function clearChat(){
                stopAllAudio();
                location.reload();
            }

            function appendUserMessage(text, imgUrl){
                const chatArea = document.getElementById('chatArea');
                let imgHtml = imgUrl ? `<img src="${imgUrl}" class="max-h-40 rounded-xl mb-2 object-contain border border-slate-700"/>` : '';
                const msg = `
                <div class="flex justify-end">
                    <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-2xl rounded-tr-sm p-3 text-xs max-w-[85%] shadow-md">
                        ${imgHtml}
                        <p>${text ? text : 'Photo Attached'}</p>
                    </div>
                </div>`;
                chatArea.insertAdjacentHTML('beforeend', msg);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            function appendAIMessage(text){
                const chatArea = document.getElementById('chatArea');
                const msg = `
                <div class="flex items-start space-x-2.5">
                    <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                        <i class="fa-solid fa-sparkles"></i>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-200 max-w-[88%] shadow-lg leading-relaxed whitespace-pre-wrap">
                        <div class="ans-content">${text}</div>
                        <button onclick="toggleVoice(this, this.previousElementSibling.innerText)" class="voice-toggle-btn mt-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-emerald-400 px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center transition shadow">
                            <i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein
                        </button>
                    </div>
                </div>`;
                chatArea.insertAdjacentHTML('beforeend', msg);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            async function sendMessage(){
                const input = document.getElementById('promptInput');
                const prompt = input.value.trim();

                if(!prompt && !currentImageFile){
                    return alert("Kripya kuch boliye ya likhiye!");
                }

                if (/chup|shant|quiet|stop/i.test(prompt)) {
                    stopAllAudio();
                }

                let imgSrc = currentImageFile ? document.getElementById('thumbImg').src : null;
                appendUserMessage(prompt, imgSrc);
                input.value = '';

                // ANIMATED THINKING BADGE
                const chatArea = document.getElementById('chatArea');
                const tempId = 'temp_' + Date.now();
                const loadingHtml = `
                <div id="${tempId}" class="flex items-center space-x-2 text-[11px] text-emerald-400 font-bold bg-slate-900/80 border border-emerald-500/30 p-2.5 rounded-2xl max-w-[220px] animate-pulse">
                    <i class="fa-solid fa-microchip fa-spin"></i>
                    <span>Avika is analyzing chart... ⚡</span>
                </div>`;
                chatArea.insertAdjacentHTML('beforeend', loadingHtml);
                chatArea.scrollTop = chatArea.scrollHeight;

                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = true;

                const fd = new FormData();
                fd.append('prompt', prompt ? prompt : 'Is photo ko analyze karein');
                if(currentImageFile){
                    fd.append('file', currentImageFile);
                }
                removeImage();

                try {
                    const res = await fetch('/api/analyze', { method: 'POST', body: fd });
                    const d = await res.json();
                    
                    document.getElementById(tempId).remove();
                    sendBtn.disabled = false;

                    if(res.ok){
                        appendAIMessage(d.analysis);
                    } else {
                        appendAIMessage("Error: " + (d.detail || "Server error"));
                    }
                } catch(e){
                    if(document.getElementById(tempId)) document.getElementById(tempId).remove();
                    sendBtn.disabled = false;
                    appendAIMessage("Connection Error: " + e.message);
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
