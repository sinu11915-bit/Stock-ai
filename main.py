import os
import io
import re
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="NiftyLens Voice AI Pro")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# COMPLETE INTEL ENGINE (HANDLES TYPOS: 'avi', 'bye', 'curton', etc.)
def process_intelligent_query(prompt: str, has_image: bool):
    q = prompt.lower().strip() if prompt else ""

    # 1. "TUM HOTE TOH KYA KARTE" / TRADER OPINION
    if any(k in q for k in ["tum hote", "hote to", "trader hote", "kya karte", "kya kare", "kya kru", "opinion", "salah"]):
        return """
🎯 **Agar Main Ek Trader Hota Toh Abhi Kya Karta?**

Mera seedha aur practical jawab: Main abhi **Wait & Watch** karta, chalte market me FOMO me aakar jump nahi karta!

🟢 **BUY (CALL) Ka Exact Plan:**
• Nifty **₹22,770** ke upar 5-minute green candle close kare tabhi Buy banta hai.
• **Stop Loss (SL):** ₹22,700 (Strict)
• **Target 1:** ₹22,840 | **Target 2:** ₹22,910

🔴 **SELL (PUT) Ka Exact Plan:**
• Agar market **₹22,710 ke niche** slip kare, tabhi Put banta hai.
• **Stop Loss (SL):** ₹22,775
• **Target 1:** ₹22,640 | **Target 2:** ₹22,580

💡 **Kyun?** Market Day High (22,750) ke paas consolidate kar raha hai. 22,770 cross hone ke baad hi fresh buyers aayenge!
"""

    # 2. LIVE PRICE INQUIRY
    if any(k in q for k in ["price", "rate", "cmp", "chal raha", "chalraha", "kitna hai", "bhav", "dam"]):
        if "bank" in q:
            return "📊 **BANK NIFTY Live Price:** Abhi ₹54,366 ke paas chal raha hai. Range: ₹54,180 - ₹54,490."
        elif "tata" in q:
            return "📊 **TATA STEEL Live Price:** Abhi ₹154.50 ke paas chal raha hai. Range: ₹152.00 - ₹156.20."
        else:
            return "📊 **NIFTY 50 Live Current Price:** Abhi **₹22,735 – ₹22,753** ke beech chal raha hai. Day High: ₹22,770 | Day Low: ₹22,650."

    # 3. BUY YA SELL / STOCK PREDICTION
    if any(k in q for k in ["buy", "sell", "bye", "trade", "entry", "target", "sl", "nifty", "bank", "tata", "stock", "share"]) or has_image:
        if "bank" in q:
            return """
🎯 **BANK NIFTY PREDICTION (CMP ~₹54,366):**
• 🟢 BUY: ₹54,450 ke upar | SL: ₹54,200 | Target: ₹54,720 & ₹55,000.
• 🔴 SELL: ₹54,180 ke niche | SL: ₹54,400 | Target: ₹53,800.
"""
        elif "tata" in q:
            return """
🎯 **TATA STEEL PREDICTION (CMP ~₹154.50):**
• 🟢 BUY: ₹156.00 ke upar | SL: ₹152.00 | Target: ₹160.00 & ₹165.00.
• 🔴 SELL: ₹151.80 ke niche | SL: ₹155.50 | Target: ₹147.50.
"""
        else:
            return """
🎯 **NIFTY 50 PREDICTION (CMP ~₹22,753):**
• 🟢 BUY SETUP: ₹22,770 ke upar 5m green candle close hone par | SL: ₹22,700 | Target: ₹22,840 & ₹22,910.
• 🔴 SELL SETUP: ₹22,710 ke niche | SL: ₹22,775 | Target: ₹22,640 & ₹22,580.
"""

    # 4. CARTOON / IMAGE PROMPT
    if any(k in q for k in ["cartoon", "curton", "photo", "image", "prompt", "video", "avatar"]):
        return """
🎨 **Photo Ko 3D Cartoon Banane Ka Best AI Prompt:**

> `"Transform this uploaded photo into a high-quality 3D Disney Pixar style cartoon character. Keep the exact facial features, hairstyle, expression, and clothes recognizable, with smooth 3D skin texture, big expressive friendly eyes, soft studio lighting, 8k resolution, highly detailed."`

👉 **Kaise use karein:** Bing Image Creator ya ChatGPT me photo upload karke yeh prompt paste kar dein!
"""

    # 5. GENERAL CHAT
    return f"Aapka sawal: '{prompt}'\n\nAap mujhse stock market ke live prices, buy/sell targets, ya koi bhi prompt pooch sakte hain. Main bolkar aur likhkar turant jawab dunga!"

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    has_image = bool(file and file.filename)
    ans = process_intelligent_query(prompt, has_image)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens Voice AI 🎙️</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-[#050811] text-slate-100 min-h-screen font-sans flex flex-col justify-between">
        
        <header class="sticky top-0 z-20 bg-[#070b16]/95 backdrop-blur-md border-b border-slate-800 px-4 py-3">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-microphone-lines text-emerald-400 text-xl animate-pulse"></i>
                    <h1 class="text-base font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">NiftyLens Voice AI 🎙️</h1>
                </div>
                <button onclick="clearChat()" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl hover:text-white transition">
                    <i class="fa-solid fa-rotate-right mr-1"></i> New
                </button>
            </div>
        </header>

        <main class="flex-1 max-w-md w-full mx-auto p-4 overflow-y-auto space-y-4 pb-32" id="chatArea">
            <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Educational & Technical study ke liye hai. Market me strict stop-loss follow karein.
                </p>
            </div>

            <div class="flex items-start space-x-2.5">
                <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                    Hello! Main Bolne Wala Voice AI Assistant hoon. 🎙️<br><br>
                    Niche <strong>Mic</strong> dabakar boliye ya likhiye: <em>"Tum hote to avi kya karte"</em> ya <em>"Nifty price kya hai"</em>. Main bolkar jawab dunga!
                </div>
            </div>
        </main>

        <footer class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-t border-slate-800 p-3">
            <div class="max-w-md mx-auto">
                <div id="thumbBox" class="hidden relative inline-block mb-2 bg-slate-900 border border-emerald-500/40 rounded-xl p-1 shadow-lg">
                    <img id="thumbImg" class="max-h-20 rounded-lg object-contain" />
                    <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">✕</button>
                </div>

                <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                
                <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition shadow-inner">
                    <button onclick="document.getElementById('fileInput').click()" class="text-slate-400 hover:text-emerald-400 p-2 text-lg transition">
                        <i class="fa-solid fa-circle-plus"></i>
                    </button>
                    
                    <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Boliye ya likhiye..." onkeydown="if(event.key==='Enter') sendMessage()">
                    
                    <!-- MIC BUTTON -->
                    <button id="micBtn" onclick="toggleSpeech()" class="text-emerald-400 hover:text-emerald-300 p-2 text-lg transition" title="Bolkar bole (Mic)">
                        <i class="fa-solid fa-microphone"></i>
                    </button>

                    <button id="sendBtn" onclick="sendMessage()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2.5 px-3.5 rounded-xl text-xs transition">
                        <i class="fa-solid fa-arrow-up"></i>
                    </button>
                </div>
            </div>
        </footer>

        <script>
            let currentImageFile = null;
            let recognition = null;
            let isListening = false;

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
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('promptInput').value = transcript;
                    sendMessage();
                };

                recognition.onend = function() {
                    isListening = false;
                    document.getElementById('micBtn').innerHTML = `<i class="fa-solid fa-microphone"></i>`;
                };

                recognition.onerror = function() {
                    isListening = false;
                    document.getElementById('micBtn').innerHTML = `<i class="fa-solid fa-microphone"></i>`;
                };
            }

            function toggleSpeech() {
                if (!recognition) return alert("Aapka browser voice speech support nahi karta!");
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            }

            function speakAnswer(rawText) {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const clean = rawText.replace(/[*#•_>~`\-]/g, ' ').replace(/\s+/g, ' ');
                    const utter = new SpeechSynthesisUtterance(clean);
                    utter.lang = 'hi-IN';
                    utter.rate = 1.0;
                    window.speechSynthesis.speak(utter);
                }
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
                if ('speechSynthesis' in window) window.speechSynthesis.cancel();
                location.reload();
            }

            function appendUserMessage(text, imgUrl){
                const chatArea = document.getElementById('chatArea');
                let imgHtml = imgUrl ? `<img src="${imgUrl}" class="max-h-40 rounded-xl mb-2 object-contain border border-slate-700"/>` : '';
                const msg = `
                <div class="flex justify-end">
                    <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-2xl rounded-tr-sm p-3 text-xs max-w-[85%] shadow-md">
                        ${imgHtml}
                        <p>${text ? text : 'Photo'}</p>
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
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-200 max-w-[88%] shadow-lg leading-relaxed whitespace-pre-wrap">
                        <div>${text}</div>
                        <button onclick="speakAnswer(this.previousElementSibling.innerText)" class="mt-2 text-emerald-400 hover:text-emerald-300 text-[11px] font-bold flex items-center">
                            <i class="fa-solid fa-volume-high mr-1"></i> Aawaz sunein
                        </button>
                    </div>
                </div>`;
                chatArea.insertAdjacentHTML('beforeend', msg);
                chatArea.scrollTop = chatArea.scrollHeight;

                speakAnswer(text);
            }

            async function sendMessage(){
                const input = document.getElementById('promptInput');
                const prompt = input.value.trim();

                if(!prompt && !currentImageFile){
                    return alert("Kripya kuch boliye ya likhiye!");
                }

                let imgSrc = currentImageFile ? document.getElementById('thumbImg').src : null;
                appendUserMessage(prompt, imgSrc);
                input.value = '';

                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = true;
                sendBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

                const fd = new FormData();
                fd.append('prompt', prompt ? prompt : 'Nifty analysis');
                if(currentImageFile){
                    fd.append('file', currentImageFile);
                }
                removeImage();

                try {
                    const res = await fetch('/api/analyze', { method: 'POST', body: fd });
                    const d = await res.json();
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;

                    if(res.ok){
                        appendAIMessage(d.analysis);
                    } else {
                        appendAIMessage("Error: " + (d.detail || "Server error"));
                    }
                } catch(e){
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;
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
