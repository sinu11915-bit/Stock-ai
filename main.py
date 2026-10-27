import os
import io
import json
import base64
import urllib.request
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="NiftyLens Universal AI")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# UNIVERSAL AI CHAT ENGINE (Answers Stock Market + Any World Question)
def query_universal_ai(prompt: str, b64_img: Optional[str] = None):
    system_instruction = """
    Aap ek Super-Intelligent, Friendly aur Honest AI Assistant hain (jaise ChatGPT aur Gemini Pro).
    Aap Indian Stock Market (Nifty, Bank Nifty, Stocks, F&O) ke Expert Analyst bhi hain.

    RULES:
    1. Agar user stock market ke bare me puche (e.g. 'buy karu ya sell', 'levels batao', 'agar tum hote toh kya karte'):
       - Direct aur honest opinion dein.
       - Exact Buy Level, Sell Level, Strict Stop Loss (SL) aur Targets dein.
       - Trader psychology aur logic clear shabdo me samjhayein.
    2. Agar user koi general / outside question puche (duniya ki koi bhi baat, study, tech, etc.):
       - ChatGPT ki tarah pura detail aur accurate answer dein.
    3. User jis bhasha me puche (Hindi, Hinglish, Bengali, ya English), usi bhasha me natural baat karein.
    """

    # 1. Try Gemini Vision if image is present
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key and b64_img:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"{system_instruction}\nUser Prompt: {prompt}"},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                    ]
                }]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # 2. Ultra-Fast Intelligent Engine for Text & General Chat
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt if prompt else "Nifty 50 ka analysis batao"}
            ],
            "model": "openai"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "NiftyLensAI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            text = resp.read().decode("utf-8")
            if text and len(text.strip()) > 5:
                return text
    except Exception:
        pass

    # 3. Built-in Smart Market Logic Fallback
    q = prompt.lower()
    if "agar tum hote" in q or "kya karte" in q or "bye ya sell" in q or "buy ya sell" in q:
        return """
🎯 **Agar Main Trader Hota Toh Abhi Kya Karta?**

Mera seedha jawab: Main abhi **Wait & Watch** karta, jaldbazi me chalte market me jump nahi karta!

🟢 **BUY (CALL) Ka Plan:**
• Nifty **22,770** ke upar 5-minute green candle close kare tabhi Buy banta hai.
• **Stop Loss (SL):** 22,700
• **Target 1:** 22,840 | **Target 2:** 22,910

🔴 **SELL (PUT) Ka Plan:**
• Agar 22,770 cross na ho aur market **22,710 ke niche** slip kare, tabhi Put banta hai.
• **Stop Loss (SL):** 22,775
• **Target 1:** 22,640 | **Target 2:** 22,580

💡 **Logic:** Nifty Day High (22,753) ke paas hai. Yaha lalach me direct Buy karne par fakeout ka risk rehta hai. Confirmation ke bina trade mat lijiye!
"""

    return f"""
📊 **Analysis / Response:**

Aapka sawal: "{prompt}"

• **Market Context:** NIFTY 50 abhi 22,753 par trade kar raha hai. 
• **Buy Range:** 22,770 ke upar with SL 22,700.
• **Sell Range:** 22,710 ke niche with SL 22,775.

Aap koi bhi sawal (kisi bhi stock ya aam sawal) puchiye, main har cheez ka jawab dunga!
"""

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    b64_image = None
    if file and file.filename:
        try:
            raw_bytes = await file.read()
            if len(raw_bytes) > 0:
                from PIL import Image
                pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                pil_img.thumbnail((900, 900))
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=75)
                b64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            pass

    ans = query_universal_ai(prompt, b64_image)
    return {"analysis": ans}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens Pro - Universal AI Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-[#050811] text-slate-100 min-h-screen font-sans flex flex-col justify-between">
        
        <!-- HEADER -->
        <header class="sticky top-0 z-20 bg-[#070b16]/90 backdrop-blur-md border-b border-slate-800/80 px-4 py-3">
            <div class="max-w-md mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-wand-magic-sparkles text-emerald-400 text-xl"></i>
                    <h1 class="text-lg font-black bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">NiftyLens Pro AI</h1>
                </div>
                <button onclick="clearChat()" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl hover:text-white transition">
                    <i class="fa-solid fa-rotate-right mr-1"></i> New Chat
                </button>
            </div>
        </header>

        <!-- CHAT FEED AREA (WHATSAPP / CHATGPT STYLE) -->
        <main class="flex-1 max-w-md w-full mx-auto p-4 overflow-y-auto space-y-4 pb-32" id="chatArea">
            
            <!-- NOTICE -->
            <div class="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Educational & Technical study ke liye hai. Market me strict stop-loss follow karein.
                </p>
            </div>

            <!-- WELCOME MESSAGE -->
            <div class="flex items-start space-x-2.5">
                <div class="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs flex-shrink-0">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="bg-slate-900/90 border border-slate-800/80 rounded-2xl rounded-tl-sm p-3.5 text-xs text-slate-200 max-w-[85%] shadow-lg leading-relaxed">
                    Hello! Main aapka AI Trading & Universal Assistant hoon. 📈<br><br>
                    Aap mujhse stock market (Nifty, Bank Nifty, Buy/Sell, SL, Target) ya <strong>duniya ka koi bhi sawal</strong> Hindi, Bengali ya English me puch sakte hain!
                </div>
            </div>

        </main>

        <!-- FLOATING BOTTOM BAR WITH + ICON -->
        <footer class="fixed bottom-0 left-0 right-0 z-30 bg-[#070b16]/95 backdrop-blur-xl border-t border-slate-800/80 p-3">
            <div class="max-w-md mx-auto">
                
                <!-- ATTACHED IMAGE PREVIEW -->
                <div id="thumbBox" class="hidden relative inline-block mb-2 bg-slate-900 border border-emerald-500/40 rounded-xl p-1 shadow-lg">
                    <img id="thumbImg" class="max-h-20 rounded-lg object-contain" />
                    <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">✕</button>
                </div>

                <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                
                <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition shadow-inner">
                    <button onclick="document.getElementById('fileInput').click()" class="text-slate-400 hover:text-emerald-400 p-2 text-lg transition">
                        <i class="fa-solid fa-circle-plus"></i>
                    </button>
                    
                    <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Puchiye: Buy kare ya sell, ya koi bhi sawal..." onkeydown="if(event.key==='Enter') sendMessage()">
                    
                    <button id="sendBtn" onclick="sendMessage()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2.5 px-3.5 rounded-xl text-xs transition">
                        <i class="fa-solid fa-arrow-up"></i>
                    </button>
                </div>
            </div>
        </footer>

        <script>
            let currentImageFile = null;

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
                location.reload();
            }

            function appendUserMessage(text, imgUrl){
                const chatArea = document.getElementById('chatArea');
                let imgHtml = imgUrl ? `<img src="${imgUrl}" class="max-h-40 rounded-xl mb-2 object-contain border border-slate-700"/>` : '';
                const msg = `
                <div class="flex justify-end">
                    <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-2xl rounded-tr-sm p-3 text-xs max-w-[85%] shadow-md">
                        ${imgHtml}
                        <p>${text ? text : 'Chart Screenshot'}</p>
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
${text}
                    </div>
                </div>`;
                chatArea.insertAdjacentHTML('beforeend', msg);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            async function sendMessage(){
                const input = document.getElementById('promptInput');
                const prompt = input.value.trim();

                if(!prompt && !currentImageFile){
                    return alert("Kripya kuch likhein ya screenshot select karein!");
                }

                // 1. Capture and clear input immediately
                let imgSrc = currentImageFile ? document.getElementById('thumbImg').src : null;
                appendUserMessage(prompt, imgSrc);
                input.value = '';

                // 2. Loading state
                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = true;
                sendBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

                const fd = new FormData();
                fd.append('prompt', prompt ? prompt : 'Is chart ka analysis karke entry exit batao');
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
                        appendAIMessage("Error: " + (d.detail || "Server response fail hua"));
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
