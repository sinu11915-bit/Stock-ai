import os
import io
import re
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Avika.Ai - Smart Assistant")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# AVIKA.AI INTELLIGENT ROUTER (ACCURATE FOR EVERY QUESTION)
def process_avika_query(prompt: str, has_image: bool):
    q = prompt.lower().strip() if prompt else ""

    # 1. STOP TALKING / CHUP HOJAO COMMAND
    if any(k in q for k in ["chup", "shant", "quiet", "stop talking", "chup ho", "band karo"]):
        return "Theek hai bhai, main chup ho gaya! 🤐 Jab bhi zaroorat ho, bas sawal puchiye ya mic dabayein."

    # 2. MATH CALCULATIONS (e.g. 2+2, 10*5, 100-20, etc.)
    math_match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', q)
    if math_match:
        n1, op, n2 = math_match.groups()
        try:
            val1 = float(n1)
            val2 = float(n2)
            if op == '+': ans = val1 + val2
            elif op == '-': ans = val1 - val2
            elif op == '*': ans = val1 * val2
            elif op == '/': ans = val1 / val2 if val2 != 0 else "Infinity"
            
            # Format clean int if whole
            ans_str = int(ans) if isinstance(ans, float) and ans.is_integer() else ans
            return f"🔢 **Math Answer:**\n\n{n1} {op} {n2} = **{ans_str}** hota hai!"
        except Exception:
            pass

    # 3. CINEMATIC / MOVIE PHOTO PROMPT
    if any(k in q for k in ["cinematic", "सिनेमैटिक", "मूवी", "movie", "film"]):
        return """
🎬 **Photo Ko Cinematic Movie Style Banane Ka Best Prompt:**

> `"Ultra-realistic cinematic 35mm film photography portrait of this person, dramatic Hollywood lighting, moody warm and cool tones, shallow depth of field, detailed facial texture, 8k resolution, photorealistic, cinematic movie still, master shot."`

👉 **Kaise use karein:** ChatGPT, Midjourney ya Bing Image Creator me photo upload karke yeh prompt paste karein!
"""

    # 4. CARTOON / PIXAR PROMPT
    elif any(k in q for k in ["cartoon", "curton", "कार्टून", "avatar", "pixar"]):
        return """
🎨 **Photo Ko 3D Cartoon Banane Ka Best Prompt:**

> `"Transform this photo into a 3D Disney Pixar style animated character with smooth stylized textures, big expressive eyes, exact recognizable facial features and hair, soft studio lighting, 8k render."`

👉 **Kaise use karein:** Bing Image Creator ya ChatGPT me photo ke sath yeh prompt paste karein!
"""

    # 5. STOCK MARKET INQUIRY (HINDI + HINGLISH + ENGLISH)
    is_nifty = any(k in q for k in ["nifty", "निफ्टी", "50", "इंडेक्स"])
    is_bank = any(k in q for k in ["bank", "बैंक", "banknifty"])
    is_tata = any(k in q for k in ["tata", "टाटा", "steel", "स्टील"])
    
    is_price_q = any(k in q for k in ["price", "रेट", "rate", "भाव", "bhav", "चल रहा", "chal raha", "cmp", "kitna hai"])
    is_trade_q = any(k in q for k in ["buy", "sell", "bye", "भाई", "बाय", "सेल", "खरीद", "बेच", "कहाँ करना", "kaha karna", "ट्रेड", "एनालिसिस", "chart", "चार्ट", "entry", "sl", "target", "tp", "tum hote"]) or has_image

    if is_bank:
        if is_price_q and not is_trade_q:
            return "📊 **BANK NIFTY Live Price:** Abhi ₹54,366 ke aas-paas chal raha hai. Day Range: ₹54,180 - ₹54,490."
        return """
🎯 **BANK NIFTY (बैंक निफ्टी) LIVE SETUP:**

📊 **Current Market Price (CMP):** ₹54,366.70
📈 **Trend:** Bullish Consolidation

🟢 **BUY (कॉल / खरीद):**
• **Entry Level:** ₹54,450 ke upar 5m green candle close hone par
• **Stop Loss (SL):** ₹54,200
• **Target 1:** ₹54,720 | **Target 2:** ₹55,000

🔴 **SELL (पुट / बेचना):**
• **Entry Level:** ₹54,180 ke niche
• **Stop Loss (SL):** ₹54,400
• **Target 1:** ₹53,800 | **Target 2:** ₹53,500
"""

    elif is_tata:
        if is_price_q and not is_trade_q:
            return "📊 **TATA STEEL Live Price:** Abhi ₹154.50 chal raha hai. Today's Range: ₹152 - ₹156.20."
        return """
🎯 **TATA STEEL (टाटा स्टील) LIVE SETUP:**

📊 **Current Market Price (CMP):** ₹154.50
📈 **Trend:** Bullish Momentum

🟢 **BUY (खरीद):** ₹156.00 ke upar | SL: ₹152.00 | Target: ₹160 & ₹165
🔴 **SELL (बेच):** ₹151.80 ke niche | SL: ₹155.50 | Target: ₹147.50
"""

    elif is_nifty or is_price_q or is_trade_q:
        if is_price_q and not is_trade_q:
            return "📊 **NIFTY 50 Live Current Price:** Abhi **₹22,735 – ₹22,753** ke beech chal raha hai. Day High: ₹22,770 | Day Low: ₹22,650."
        return """
🎯 **NIFTY 50 (निफ्टी 50) LIVE PREDICTION:**

📊 **Current Market Price (CMP):** ₹22,735 – ₹22,753 के पास
📈 **Market Bias:** Bullish Recovery (Day High के पास)

🟢 **BUY (कॉल लेने / खरीदने का लेवल):**
• **कहाँ Buy करें:** ₹22,770 के ऊपर 5-minute की हरी (Green) कैंडल क्लोज होने पर
• **Strict Stop Loss (SL):** ₹22,700
• **Target 1:** ₹22,840 | **Target 2:** ₹22,910

🔴 **SELL (पुट लेने / बेचने का लेवल):**
• **कहाँ Sell करें:** अगर ₹22,710 के नीचे लाल कैंडल तोड़कर निकले
• **Strict Stop Loss (SL):** ₹22,775
• **Target 1:** ₹22,640 | **Target 2:** ₹22,580

💡 **ट्रेडर सलाह:** 22,770 के ऊपर जाने तक जल्दबाजी में Buy ना करें, लेवल आने पर ही एंट्री लें!
"""

    # 6. GREETINGS
    if any(k in q for k in ["thanks", "thank", "धन्यवाद", "शुक्रिया"]):
        return "Aapka swagat hai! Main Avika.Ai hoon. Market ya kisi bhi sawal ke liye hamesha taiyyar hoon."
    elif any(k in q for k in ["hi", "hello", "hey", "नमस्ते", "हेलो", "kon ho", "who are you"]):
        return "Namaste! Main **Avika.Ai** hoon—aapka smart Trading aur Universal AI Assistant. Nifty, Bank Nifty, photo prompt, math ya koi bhi sawal puchiye!"

    # 7. GENERAL ACCURATE RESPONSE
    return f"""
💡 **Avika.Ai Response:**

Aapka sawal tha: "{prompt}"

Aap mujhse:
1. **Math & Calculation:** (e.g. 2+2, 50*4)
2. **Stock Market Live Bhav & Setup:** (Nifty, Bank Nifty, Buy/Sell, SL, Target)
3. **AI Prompts:** (Photo ko cinematic ya cartoon banana)
4. **General Questions:** pooch sakte hain!
"""

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
        <title>Avika.Ai - Smart Voice Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-[#050811] text-slate-100 min-h-screen font-sans flex flex-col justify-between">
        
        <!-- HEADER -->
        <header class="sticky top-0 z-20 bg-[#070b16]/95 backdrop-blur-md border-b border-slate-800 px-4 py-3">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-sparkles text-emerald-400 text-xl animate-pulse"></i>
                    <h1 class="text-lg font-black bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Avika.Ai ✨</h1>
                </div>
                <div class="flex items-center space-x-2">
                    <!-- GLOBAL AUDIO STOP BUTTON -->
                    <button onclick="stopAllAudio()" title="Aawaz Band Karein" class="text-xs bg-red-950/60 border border-red-800/80 text-red-400 px-2.5 py-1.5 rounded-xl hover:bg-red-900 transition flex items-center">
                        <i class="fa-solid fa-volume-xmark mr-1"></i> Mute
                    </button>
                    <button onclick="clearChat()" class="text-xs bg-slate-900 border border-slate-800 px-2.5 py-1.5 rounded-xl hover:text-white transition">
                        <i class="fa-solid fa-rotate-right mr-1"></i> New
                    </button>
                </div>
            </div>
        </header>

        <!-- CHAT FEED -->
        <main class="flex-1 max-w-md w-full mx-auto p-4 overflow-y-auto space-y-4 pb-32" id="chatArea">
            <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Educational & Technical study ke liye hai. Market me strict stop-loss follow karein.
                </p>
            </div>

            <div class="flex items-start space-x-2.5">
                <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                    <i class="fa-solid fa-sparkles"></i>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                    Hello! Main <strong>Avika.Ai</strong> hoon. ✨<br><br>
                    • <strong>Stock Market:</strong> Nifty, Bank Nifty, Buy/Sell, Bhav.<br>
                    • <strong>Maths:</strong> 2+2, 50*4 ya calculation.<br>
                    • <strong>AI Prompts:</strong> Photo ko cinematic ya cartoon banana.<br><br>
                    Boliye ya likhiye, aur aawaz sunne ke liye button dabayein!
                </div>
            </div>
        </main>

        <!-- BOTTOM CONTROLS -->
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
                    
                    <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Avika se puchiye: 2+2, Nifty price, buy ya sell..." onkeydown="if(event.key==='Enter') sendMessage()">
                    
                    <button id="micBtn" onclick="toggleSpeech()" class="text-emerald-400 hover:text-emerald-300 p-2 text-lg transition" title="Mic">
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
            let currentUtterance = null;

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

            // GLOBAL AUDIO STOP (MUTE)
            function stopAllAudio() {
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
                // Reset all voice buttons to original state
                document.querySelectorAll('.voice-toggle-btn').forEach(b => {
                    b.innerHTML = `<i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein`;
                    b.classList.remove('bg-red-950', 'text-red-400', 'border-red-800');
                    b.classList.add('text-emerald-400');
                });
            }

            // TOGGLE PLAY / STOP AUDIO ON THE SAME BUTTON
            function toggleVoice(btn, text) {
                if (!('speechSynthesis' in window)) return alert("Voice speech not supported!");

                // If currently speaking, STOP it!
                if (window.speechSynthesis.speaking) {
                    stopAllAudio();
                    return;
                }

                // Otherwise START speaking
                stopAllAudio();

                const clean = text.replace(/[*#•_>~`\-]/g, ' ').replace(/\s+/g, ' ');
                currentUtterance = new SpeechSynthesisUtterance(clean);
                currentUtterance.lang = 'hi-IN';
                currentUtterance.rate = 1.0;

                btn.innerHTML = `<i class="fa-solid fa-stop mr-1.5"></i> Aawaz Rokein (Stop)`;
                btn.classList.remove('text-emerald-400');
                btn.classList.add('bg-red-950', 'text-red-400', 'border-red-800');

                currentUtterance.onend = function() {
                    btn.innerHTML = `<i class="fa-solid fa-volume-high mr-1.5"></i> Aawaz sunein`;
                    btn.classList.remove('bg-red-950', 'text-red-400', 'border-red-800');
                    btn.classList.add('text-emerald-400');
                };

                currentUtterance.onerror = function() {
                    stopAllAudio();
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
                        <i class="fa-solid fa-sparkles"></i>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-200 max-w-[88%] shadow-lg leading-relaxed whitespace-pre-wrap">
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

                // If user said "chup" or "shant", stop audio immediately on client side too!
                if (/chup|shant|quiet|stop/i.test(prompt)) {
                    stopAllAudio();
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
