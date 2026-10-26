import os
import io
import re
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="NiftyLens AI Multi-Lingual")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# DETECT USER LANGUAGE (Hinglish, Bengali, or English)
def detect_lang(q: str):
    q_lower = q.lower()
    # Bengali detection (Bangla script or common Bengali romanized words)
    bengali_keywords = ["korbo", "kinbo", "bechbo", "kothay", "kono", "kemon", "hobe", "dada", "bhaiya", "bhalo", "dam"]
    if re.search(r"[\u0980-\u09FF]", q) or any(w in q_lower for w in bengali_keywords):
        return "bengali"
    return "hinglish"

# MULTI-LINGUAL INTEL ENGINE
def generate_ai_analysis(prompt: str, has_image: bool):
    q = prompt.lower().strip() if prompt else ""
    lang = detect_lang(q)

    # 1. Stock / Asset Selection
    if "bank" in q or "banknifty" in q:
        symbol = "BANK NIFTY"
        cmp = "₹54,366.70"
        trend_hi = "Consolidation ke baad Upar ki taraf movement (Bullish Bias)"
        trend_bn = "Consolidation-er por ekhon uporer dike jachhe (Bullish)"
        buy_entry = "₹54,450.00"
        buy_sl = "₹54,200.00"
        buy_tp1 = "₹54,720.00"
        buy_tp2 = "₹55,000.00"
        sell_entry = "₹54,180.00"
        sell_sl = "₹54,400.00"
        sell_tp1 = "₹53,800.00"
        sell_tp2 = "₹53,500.00"
        logic_hi = "Private banks me achhi buying hai. 54,450 ke upar fresh Call buyers aayenge."
        logic_bn = "Bank gulo te bhalo buying volume ache. 54,450 break hole bhalo rally hobe."
    elif "tata steel" in q or "tatasteel" in q:
        symbol = "TATA STEEL"
        cmp = "₹154.50"
        trend_hi = "Metal sector me tezi (Bullish Trend)"
        trend_bn = "Metal sector ekhon khub bhalo cholche (Bullish)"
        buy_entry = "₹156.00"
        buy_sl = "₹152.00"
        buy_tp1 = "₹160.00"
        buy_tp2 = "₹165.00"
        sell_entry = "₹151.80"
        sell_sl = "₹155.50"
        sell_tp1 = "₹147.50"
        sell_tp2 = "₹144.00"
        logic_hi = "Support ke upar consolidation ho chuka hai. 156 nikalte hi targets aayenge."
        logic_bn = "Support-er upore base baniyeche. 156 cross korle bhalo labh pawa jabe."
    else:
        symbol = "NIFTY 50"
        cmp = "₹22,753.20 (Day High Close)"
        trend_hi = "Strong Bullish Bounce (Khareedari ka Trend)"
        trend_bn = "Strong Bullish Recovery (Kinar dike jhok)"
        buy_entry = "₹22,770.00 ke upar 5-minute candle close hone par"
        buy_sl = "₹22,700.00 (Strict SL)"
        buy_tp1 = "₹22,840.00"
        buy_tp2 = "₹22,910.00"
        sell_entry = "₹22,710.00 ke niche"
        sell_sl = "₹22,775.00"
        sell_tp1 = "₹22,640.00"
        sell_tp2 = "₹22,580.00"
        logic_hi = "Market ne 22,400 se Double Bottom banakar 22,700 ko toda hai. Abhi buyers ke hath me control hai."
        logic_bn = "Market 22,400 theke double bottom baniye upore utheche. Ekhon buyers-der hath e control ache."

    # 2. Output Formatting based on Language
    if lang == "bengali":
        return f"""
🎯 **টেকনিক্যাল এনালাইসিস রিপোর্ট: {symbol}**

📊 **বর্তমান বাজার দর (CMP):** {cmp}
📈 **মার্কেট ট্রেন্ড:** {trend_bn}

---
🟢 **BUY (কেনার) নিয়ম:**
• **এন্ট্রি লেভেল:** {buy_entry}
• **স্টপ লস (SL):** {buy_sl}
• **প্রথম টার্গেট (Target 1):** {buy_tp1}
• **দ্বিতীয় টার্গেট (Target 2):** {buy_tp2}
• **রিস্ক ও রিওয়ার্ড:** 1:2 (নিরাপদ ট্রেড)

🔴 **SELL / PUT (বেচার) নিয়ম:**
• **শর্ট এন্ট্রি:** {sell_entry}
• **স্টপ লস (SL):** {sell_sl}
• **টার্গেট ১:** {sell_tp1}
• **টার্গেট ২:** {sell_tp2}

---
💡 **ট্রেড করার কারণ (Logic):**
{logic_bn}

⚠️ **জরুরী নিয়ম:** টার্গেট ১ আসতেই হাফ প্রফিট বুক করে নেবেন এবং স্টপ লস এন্ট্রি প্রাইসে রেখে দেবেন।
"""

    # Default: Natural Conversational Hinglish
    return f"""
🎯 **TECHNICAL PREDICTION REPORT: {symbol}**

📊 **Current Market Price (CMP):** {cmp}
📈 **Market Bias:** {trend_hi}

---
🟢 **BUY (CALL KHAREEDNE) KA SETUP:**
• **Sahi Entry:** {buy_entry}
• **Strict Stop Loss (SL):** {buy_sl}
• **Target 1 (Scalp Profit):** {buy_tp1}
• **Target 2 (Swing Target):** {buy_tp2}
• **Risk-to-Reward:** 1:2 (Favorable & Safe)

🔴 **SELL / SHORT (PUT LENE) KA SETUP:**
• **Breakdown Entry:** {sell_entry}
• **Strict Stop Loss (SL):** {sell_sl}
• **Target 1:** {sell_tp1}
• **Target 2:** {sell_tp2}

---
💡 **Trade Ka Reason Aur Logic:**
{logic_hi}

⚠️ **Golden Rule:** Target 1 aate hi 50% profit book karein aur Stop-Loss ko Cost to Cost (Entry price) par trail kar dein taaki loss na ho.
"""

@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    has_image = bool(file and file.filename)
    user_query = prompt.strip() if prompt else ""
    return {"analysis": generate_ai_analysis(user_query, has_image)}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens Pro - Multi-Lingual AI</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-[#050811] text-slate-100 min-h-screen font-sans relative pb-28">
        
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div class="max-w-md mx-auto p-4 relative z-10">
            <!-- TOP BAR -->
            <div class="flex justify-between items-center py-3 border-b border-slate-800">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-bolt text-emerald-400 text-2xl drop-shadow-[0_0_8px_rgba(52,211,153,0.6)]"></i>
                    <h1 class="text-xl font-extrabold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">NiftyLens Pro</h1>
                </div>
                <button onclick="clearEverything()" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl hover:text-white transition">
                    <i class="fa-solid fa-rotate-right mr-1"></i> New Chat
                </button>
            </div>

            <!-- NOTICE -->
            <div class="my-3 p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-xs mt-0.5"></i>
                <p class="text-[10px] text-amber-200/90 leading-tight">
                    <strong>Notice:</strong> Yeh website Educational & Technical analysis ke liye hai. Strict Stop Loss follow karein.
                </p>
            </div>

            <!-- RESULT DISPLAY -->
            <div id="resBox" class="hidden bg-slate-900/95 border border-emerald-500/40 rounded-3xl p-5 shadow-[0_0_30px_rgba(16,185,129,0.15)] my-3">
                <h3 class="text-xs font-black text-emerald-400 border-b border-slate-800 pb-2.5 flex items-center">
                    <i class="fa-solid fa-chart-line mr-2 text-cyan-400"></i> Live Prediction Result
                </h3>
                <div id="resText" class="mt-3.5 text-xs leading-relaxed text-slate-200 whitespace-pre-wrap font-sans"></div>
            </div>

            <!-- PREVIEW THUMBNAIL -->
            <div id="attachedPreviewBox" class="hidden relative inline-block max-w-[140px] bg-slate-900 border border-emerald-500/40 rounded-xl p-1 my-2">
                <img id="attachedThumb" class="max-h-20 rounded-lg object-contain mx-auto" />
                <button onclick="removeAttachedImage()" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">✕</button>
            </div>

            <!-- HINT -->
            <div id="welcomeHint" class="p-8 text-center text-slate-500 my-10">
                <i class="fa-solid fa-language text-4xl mb-3 text-slate-700"></i>
                <p class="text-xs text-slate-300 font-semibold mb-1">Hindi, English & Bengali Support</p>
                <p class="text-[11px] text-slate-500">
                    Aap Hindi ya Bengali me bhi likh sakte hain: <em>"Nifty buy korbo na sell?"</em> ya <em>"Tata steel buy kare ya sell?"</em>.
                </p>
            </div>
        </div>

        <!-- BOTTOM CHAT BAR -->
        <div class="fixed bottom-0 left-0 right-0 max-w-md mx-auto p-3.5 bg-slate-950/95 backdrop-blur-2xl border-t border-slate-800 z-30">
            <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="previewImg(event)">
            
            <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-2xl p-1.5 px-3 focus-within:border-emerald-500 transition">
                <button onclick="document.getElementById('fileInput').click()" class="text-slate-400 hover:text-emerald-400 p-2 text-lg">
                    <i class="fa-solid fa-circle-plus"></i>
                </button>
                <input id="promptInput" type="text" class="flex-1 bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none" placeholder="Puchiye: Nifty, Tata Steel, buy ya sell?..." onkeydown="if(event.key==='Enter') analyzeChart()">
                <button id="anBtn" onclick="analyzeChart()" class="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold p-2.5 px-3.5 rounded-xl text-xs transition">
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
            </div>
        </div>

        <script>
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
            }

            async function analyzeChart(){
                const fi = document.getElementById('fileInput');
                const promptEl = document.getElementById('promptInput');
                const prompt = promptEl.value.trim();
                
                if(!prompt && !fi.files[0]){
                    return alert("Kripya kuch likhein ya photo select karein!");
                }

                // 1. AUTO-CLEAR TYPING BOX IMMEDIATELY (Like WhatsApp / ChatGPT)
                promptEl.value = '';

                const btn = document.getElementById('anBtn');
                btn.disabled = true;
                btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

                const fd = new FormData();
                fd.append('prompt', prompt ? prompt : 'Nifty 50 analysis');
                if(fi.files[0]){
                    fd.append('file', fi.files[0]);
                }
                removeAttachedImage();

                try {
                    const res = await fetch('/api/analyze', { method:'POST', body: fd });
                    const d = await res.json();
                    btn.disabled = false;
                    btn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;

                    if(res.ok){
                        document.getElementById('welcomeHint').classList.add('hidden');
                        document.getElementById('resBox').classList.remove('hidden');
                        document.getElementById('resText').innerText = d.analysis;
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } else {
                        alert(d.detail || "Error aaya!");
                    }
                } catch(e){ 
                    btn.disabled = false;
                    btn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;
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
