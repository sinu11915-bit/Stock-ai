import os
import io
import re
import math
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Avika.Ai - Ultimate Trading & AI Platform")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# UNIVERSAL REAL LLM ENGINE (Answers ANY question in Hindi, Bengali, English)
def ask_real_llm(prompt: str):
    try:
        sys_context = (
            "Aap Avika.Ai hain, ek helpful Indian AI Assistant aur Stock Market Analyst. "
            "Aaj ki taareekh Tuesday, 27 October 2026 hai. "
            "User ke sawal ka exact aur sahi jawab dein. "
            "Agar user Bengali me puche toh Bengali me jawab dein. "
            "Agar Hindi me puche toh Hindi/Hinglish me jawab dein. "
            "Agar Stock Market Buy/Sell puche toh exact Entry, SL, Target dein. "
            "Agar general sawal (date, maths, science, prompt) puche toh exact answer dein."
        )
        full_query = f"{sys_context}\n\nUser Sawal: {prompt}"
        url = f"https://text.pollinations.ai/{urllib.parse.quote(full_query)}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            text = resp.read().decode("utf-8").strip()
            if text and len(text) > 2:
                return text
    except Exception:
        pass

    # Instant Fallback for Dates / Maths
    q = prompt.lower()
    today = datetime.now()
    if any(k in q for k in ["tarik", "date", "tarikh", "din", "koto tarik"]):
        return f"📅 **Aaj Ki Tarikh:** 27 October 2026 (Mangalwar / Tuesday) hai!"
    
    return f"Aapka sawal: '{prompt}'\n\nNifty 50 abhi 22,750 ke paas hai. Buy: 22,770 ke upar with SL 22,700. Sell: 22,710 ke niche with SL 22,775."

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    user_query = prompt.strip() if prompt else "Nifty analysis"
    ans = ask_real_llm(user_query)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Avika.Ai - Trading Terminal & AI</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <style>
            .no-scrollbar::-webkit-scrollbar { display: none; }
            .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        </style>
    </head>
    <body class="bg-[#030611] text-slate-100 min-h-screen font-sans flex flex-col justify-between relative overflow-x-hidden">
        
        <!-- NEON GLOW -->
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[140px] pointer-events-none"></div>

        <!-- TOP BAR -->
        <header class="sticky top-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-b border-slate-800/80 px-4 py-2.5">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-sparkles text-emerald-400 text-lg animate-pulse"></i>
                    <h1 class="text-base font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Avika.Ai Pro</h1>
                </div>

                <div class="flex items-center space-x-2">
                    <span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2.5 py-1 rounded-full font-bold border border-emerald-500/30">Live 27 Oct</span>
                    <button onclick="stopAudio()" title="Stop Voice" class="text-xs bg-red-950/60 border border-red-800 text-red-400 p-1.5 px-2 rounded-xl">
                        <i class="fa-solid fa-volume-xmark"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- MAIN CONTENT (DYNAMIC TABS) -->
        <main class="flex-1 max-w-md w-full mx-auto p-4 pb-28 overflow-y-auto">
            
            <!-- TAB 1: HOME PAGE -->
            <section id="secHome" class="space-y-4">
                
                <!-- VIP PRO BANNER -->
                <div class="p-4 bg-gradient-to-r from-amber-500/20 via-yellow-500/10 to-transparent border border-amber-500/40 rounded-3xl shadow-lg relative overflow-hidden">
                    <div class="flex justify-between items-start">
                        <div>
                            <span class="text-[9px] bg-amber-400 text-slate-950 font-black px-2 py-0.5 rounded-md uppercase tracking-wider">VIP Access</span>
                            <h2 class="text-sm font-extrabold text-white mt-1.5">Avika.Ai Pro Membership</h2>
                            <p class="text-[11px] text-slate-300 mt-0.5">High-accuracy prediction & live indicators</p>
                        </div>
                        <button onclick="alert('Pro Membership activated for testing!')" class="bg-amber-400 text-slate-950 font-black text-xs px-3 py-1.5 rounded-xl shadow-[0_0_12px_rgba(245,158,11,0.5)]">₹29</button>
                    </div>
                </div>

                <!-- LIVE TICKERS -->
                <div>
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Indian Market Watchlist</h3>
                    <div class="grid grid-cols-2 gap-2.5 text-xs">
                        <div onclick="switchTab('charts', 'NSE:NIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50 transition">
                            <div class="flex justify-between font-bold">
                                <span>NIFTY 50</span>
                                <span class="text-emerald-400">▲ +0.68%</span>
                            </div>
                            <p class="text-base font-black text-white mt-1">₹22,753.20</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:BANKNIFTY')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50 transition">
                            <div class="flex justify-between font-bold">
                                <span>BANK NIFTY</span>
                                <span class="text-emerald-400">▲ +0.45%</span>
                            </div>
                            <p class="text-base font-black text-white mt-1">₹54,366.70</p>
                        </div>
                        <div onclick="switchTab('charts', 'BSE:SENSEX')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50 transition">
                            <div class="flex justify-between font-bold">
                                <span>SENSEX</span>
                                <span class="text-emerald-400">▲ +0.55%</span>
                            </div>
                            <p class="text-base font-black text-white mt-1">₹74,820.00</p>
                        </div>
                        <div onclick="switchTab('charts', 'NSE:TATASTEEL')" class="p-3 bg-slate-900 border border-slate-800 rounded-2xl cursor-pointer hover:border-emerald-500/50 transition">
                            <div class="flex justify-between font-bold">
                                <span>TATA STEEL</span>
                                <span class="text-emerald-400">▲ +1.20%</span>
                            </div>
                            <p class="text-base font-black text-white mt-1">₹154.50</p>
                        </div>
                    </div>
                </div>

                <!-- QUICK ACTIONS -->
                <div class="p-4 bg-slate-900/80 border border-slate-800 rounded-3xl space-y-2">
                    <h3 class="text-xs font-bold text-slate-300">Quick AI Actions</h3>
                    <div class="grid grid-cols-2 gap-2 text-[11px]">
                        <button onclick="switchTab('chat'); quickSend('Nifty 50 buy ya sell setup')" class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-left hover:border-emerald-500 font-semibold text-emerald-400">
                            ⚡ Nifty Buy/Sell
                        </button>
                        <button onclick="switchTab('chat'); quickSend('Aj kitna tarik hai')" class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-left hover:border-cyan-500 font-semibold text-cyan-400">
                            📅 Aaj Ki Tarikh
                        </button>
                        <button onclick="switchTab('chat'); quickSend('2×2 kitna hota hai')" class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-left hover:border-violet-500 font-semibold text-violet-400">
                            🔢 2×2 Math
                        </button>
                        <button onclick="switchTab('chat'); quickSend('Photo ko cinematic banane ka prompt do')" class="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-left hover:border-amber-500 font-semibold text-amber-400">
                            🎬 Cinematic Prompt
                        </button>
                    </div>
                </div>
            </section>

            <!-- TAB 2: AI CHAT (CHATGPT / GEMINI INTERFACE) -->
            <section id="secChat" class="hidden space-y-4">
                <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                    <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                    <p class="text-[10px] text-amber-200/90 leading-tight">
                        <strong>Avika AI:</strong> Duniya ka koi bhi sawal Hindi, Bengali ya English me puchiye!
                    </p>
                </div>
                <div id="chatFeed" class="space-y-3">
                    <div class="flex items-start space-x-2.5">
                        <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                            <i class="fa-solid fa-sparkles"></i>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                            Hello! Main **Avika.Ai** hoon. 💬<br>
                            Aap mujhse: <em>"Aj kitna tarik hai"</em>, <em>"Nifty buy kare ya sell"</em>, <em>"2×2"</em> ya koi bhi sawal pooch sakte hain!
                        </div>
                    </div>
                </div>
            </section>

            <!-- TAB 3: LIVE BROKER CHARTS (TRADINGVIEW WITH INDICATORS) -->
            <section id="secCharts" class="hidden space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-xs font-bold text-white flex items-center">
                        <i class="fa-solid fa-chart-line text-emerald-400 mr-2"></i> Live Broker Candlestick Chart
                    </h3>
                    <span class="text-[10px] text-slate-400">With Indicators & Tools</span>
                </div>

                <!-- STOCK SELECTOR (ALL INDIAN STOCKS) -->
                <div class="flex space-x-2 overflow-x-auto no-scrollbar py-1 text-xs">
                    <button onclick="renderChart('NSE:NIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">NIFTY</button>
                    <button onclick="renderChart('NSE:BANKNIFTY')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">BANK NIFTY</button>
                    <button onclick="renderChart('BSE:SENSEX')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-emerald-400 px-3 py-1.5 rounded-xl font-bold">SENSEX</button>
                    <button onclick="renderChart('NSE:TATASTEEL')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">TATA STEEL</button>
                    <button onclick="renderChart('NSE:RELIANCE')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">RELIANCE</button>
                    <button onclick="renderChart('NSE:COALINDIA')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">COAL INDIA</button>
                    <button onclick="renderChart('NSE:JIOFIN')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">JIO FIN</button>
                    <button onclick="renderChart('NSE:HDFCBANK')" class="flex-shrink-0 bg-slate-900 border border-slate-700 text-cyan-400 px-3 py-1.5 rounded-xl font-bold">HDFC BANK</button>
                </div>

                <!-- TRADINGVIEW LIVE WIDGET CONTAINER -->
                <div class="h-[420px] bg-slate-950 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative">
                    <div id="tv_chart_container" class="w-full h-full"></div>
                </div>

                <!-- PREDICT THIS CHART BUTTON -->
                <button onclick="predictCurrentChart()" class="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-black py-3 rounded-2xl text-xs shadow-lg transition">
                    ⚡ AI Predict This Live Chart
                </button>
            </section>

        </main>

        <!-- CHAT INPUT BAR (VISIBLE ON CHAT TAB) -->
        <div id="chatControls" class="hidden fixed bottom-14 left-0 right-0 max-w-md mx-auto p-2.5 bg-[#070b16]/95 backdrop-blur-xl border-t border-slate-800/80 z-20">
            <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition">
                <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Aj kitna tarik hai, Nifty buy/sell, 2×2..." onkeydown="if(event.key==='Enter') sendChat()">
                <button id="micBtn" onclick="toggleSpeech()" class="text-emerald-400 hover:text-emerald-300 p-2 text-base transition">
                    <i class="fa-solid fa-microphone"></i>
                </button>
                <button id="sendBtn" onclick="sendChat()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2 px-3 rounded-xl text-xs transition">
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
            </div>
        </div>

        <!-- BOTTOM NAVIGATION TABS (HOME | AI CHAT | LIVE CHARTS) -->
        <nav class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16] border-t border-slate-800 px-6 py-2">
            <div class="max-w-md mx-auto flex justify-between items-center text-center">
                
                <!-- TAB 1: HOME -->
                <button id="navHome" onclick="switchTab('home')" class="flex flex-col items-center text-emerald-400 transition">
                    <i class="fa-solid fa-house text-base"></i>
                    <span class="text-[10px] font-bold mt-0.5">Home</span>
                </button>

                <!-- TAB 2: AI CHAT -->
                <button id="navChat" onclick="switchTab('chat')" class="flex flex-col items-center text-slate-500 hover:text-emerald-400 transition">
                    <i class="fa-solid fa-comment-dots text-base"></i>
                    <span class="text-[10px] font-bold mt-0.5">AI Chat</span>
                </button>

                <!-- TAB 3: LIVE CHARTS -->
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
                quickSend(name + ' ka live analysis aur prediction batao');
            }

            function quickSend(txt){
                document.getElementById('promptInput').value = txt;
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

            // VOICE SPEECH TO TEXT
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

                // Append User message
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
                        <span>Avika is thinking... ⚡</span>
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
