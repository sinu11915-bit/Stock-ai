import os
import io
import sqlite3
import hashlib
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image
from pydantic import BaseModel

app = FastAPI(title="NiftyLens AI Pro")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

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

@app.post("/api/register")
def register(data: RegisterData):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        hashed = hash_password(data.password)
        c.execute("INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
                  (data.email.strip().lower(), data.phone.strip(), hashed))
        conn.commit()
        conn.close()
        return {"message": "Registration successful! Ab Login karein."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Yeh Email ya Mobile pehle se registered hai!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/login")
def login(data: LoginData):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT email, password FROM users WHERE email=? OR phone=?", 
                  (data.identifier.strip().lower(), data.identifier.strip()))
        user = c.fetchone()
        conn.close()
        
        if not user or user[1] != hash_password(data.password):
            raise HTTPException(status_code=400, detail="Galat Email/Phone ya Password!")
        
        return {"token": "authenticated_user", "email": user[0]}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    prompt: str = Form("")
):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY Render par configure nahi hai!")

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        system_prompt = f"""
        Aap ek Elite Indian Stock Market Quantitative & Technical Analyst hain (NSE/BSE/Nifty/BankNifty).
        User Sawal: {prompt if prompt else 'Pichle 1 Mahine, 1 Hafte aur Live chart ke hisab se exact Buy/Sell prediction do.'}

        Is chart ko scan karke Y-axis ke real numbers ke hisab se niche diye format me ek professional report banayein:

        📅 1. PAST 1 MONTH MACRO CONTEXT:
        - Monthly High / Low range jo chart me detect ho rahi hai.
        - Overall monthly structure: (Uptrend / Downtrend / Consolidation).

        📊 2. PAST 1 WEEK MOMENTUM:
        - Pichle 1 hafte ke swings (Higher Highs ya Lower Lows).
        - Major Breakdown ya Reversal zone.

        ⚡ 3. LIVE INTRADAY PRICE ACTION (Current Price):
        - Current Market Price (CMP) jo right side Y-axis par dikh rahi hai.
        - Candlestick pattern (Rejection wick, breakout candle, consolidation).

        🎯 4. ACTIONABLE TRADE PREDICTION:
        - 🟢 SAFE BUY ENTRY: (Exact price jiske upar green candle close par buy banta hai)
        - 🔴 SAFE SELL/SHORT ENTRY: (Exact price jiske niche breakdown par sell/put banta hai)
        - 🛑 STRICT STOP LOSS (SL): (Both sides ke liye risk management)
        - 🏁 TARGET 1 (Scalp):
        - 🏁 TARGET 2 (Positional / Swing):
        - ⚖️ RISK-TO-REWARD RATIO: (e.g. 1:2 ya 1:2.5)

        ⚠️ 5. RISK DISCLAIMER:
        - "Technical observation for educational research. Follow strict stop-loss."
        """

        models_to_try = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-2.5-flash"]
        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[image, system_prompt]
                )
                if response and response.text:
                    return {"analysis": response.text}
            except Exception as ex:
                last_error = ex
                continue

        raise HTTPException(status_code=500, detail=f"Model Error: {str(last_error)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens AI Pro</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
        <div class="max-w-md mx-auto p-4 min-h-screen flex flex-col justify-between">
            <div class="flex justify-between items-center py-3 border-b border-slate-800">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-chart-pie text-emerald-400 text-2xl"></i>
                    <h1 class="text-xl font-bold tracking-wider">NiftyLens AI Pro</h1>
                </div>
                <button id="logoutBtn" onclick="logout()" class="hidden text-xs bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg">Logout</button>
            </div>

            <!-- AUTH BOX -->
            <div id="authSection" class="my-auto py-6">
                <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl">
                    <div class="flex justify-center space-x-6 mb-6 border-b border-slate-800 pb-2">
                        <button id="tabL" onclick="switchTab('login')" class="text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1">Login</button>
                        <button id="tabR" onclick="switchTab('reg')" class="text-slate-400 font-semibold pb-1">Register</button>
                    </div>

                    <div id="loginForm" class="space-y-4">
                        <div>
                            <label class="text-xs text-slate-400">Email ya Mobile</label>
                            <input id="lId" type="text" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="user@gmail.com ya 9876543210">
                        </div>
                        <div>
                            <label class="text-xs text-slate-400">Password</label>
                            <input id="lPass" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="••••••••">
                        </div>
                        <button id="lBtn" onclick="loginUser()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3 rounded-xl transition">Login</button>
                    </div>

                    <div id="regForm" class="space-y-4 hidden">
                        <div>
                            <label class="text-xs text-slate-400">Email</label>
                            <input id="rEmail" type="email" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="user@gmail.com">
                        </div>
                        <div>
                            <label class="text-xs text-slate-400">Mobile Number</label>
                            <input id="rPhone" type="tel" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="9876543210">
                        </div>
                        <div>
                            <label class="text-xs text-slate-400">Password</label>
                            <input id="rPass" type="password" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="••••••••">
                        </div>
                        <button id="rBtn" onclick="registerUser()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3 rounded-xl transition">Register</button>
                    </div>
                </div>
            </div>

            <!-- DASHBOARD -->
            <div id="dashSection" class="hidden flex-1 py-4 flex flex-col space-y-4">
                <div class="border-2 border-dashed border-slate-800 hover:border-emerald-500 rounded-2xl p-4 text-center cursor-pointer bg-slate-900/60" onclick="document.getElementById('fileInput').click()">
                    <input id="fileInput" type="file" accept="image/*" class="hidden" onchange="previewImg(event)">
                    <div id="uBox">
                        <i class="fa-solid fa-cloud-arrow-up text-3xl text-emerald-400 mb-2"></i>
                        <p class="text-sm font-semibold text-slate-200">Chart Screenshot Upload Karein</p>
                        <p class="text-xs text-slate-500 mt-1">Tap karein gallery ke liye</p>
                    </div>
                    <img id="preview" class="hidden max-h-52 mx-auto rounded-lg shadow-lg mt-2 object-contain" />
                </div>

                <div>
                    <label class="text-xs text-slate-400">Aapka Sawal / Analysis Prompt</label>
                    <input id="promptInput" type="text" class="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="e.g. Pichle 1 mahine aur 1 hafte ke hisab se prediction do">
                </div>

                <button id="anBtn" onclick="analyzeChart()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3.5 rounded-xl shadow-lg transition">
                    <i class="fa-solid fa-wand-magic-sparkles mr-2"></i> 1-Month + 1-Week Deep Prediction
                </button>

                <div id="resBox" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-4 mt-2">
                    <h3 class="text-sm font-bold text-emerald-400 border-b border-slate-800 pb-2 flex items-center">
                        <i class="fa-solid fa-brain mr-2"></i> Deep Multi-Timeframe Prediction
                    </h3>
                    <div id="resText" class="mt-3 text-xs leading-relaxed text-slate-200 whitespace-pre-wrap"></div>
                </div>
            </div>

            <div class="text-center py-2 text-[10px] text-slate-600">
                NiftyLens AI Pro &bull; Advanced Technical Analysis
            </div>
        </div>

        <script>
            function switchTab(t) {
                if(t==='login'){
                    document.getElementById('loginForm').classList.remove('hidden');
                    document.getElementById('regForm').classList.add('hidden');
                    document.getElementById('tabL').className = "text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1";
                    document.getElementById('tabR').className = "text-slate-400 font-semibold pb-1";
                } else {
                    document.getElementById('loginForm').classList.add('hidden');
                    document.getElementById('regForm').classList.remove('hidden');
                    document.getElementById('tabR').className = "text-emerald-400 font-bold border-b-2 border-emerald-400 pb-1";
                    document.getElementById('tabL').className = "text-slate-400 font-semibold pb-1";
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
                    if(res.ok){ 
                        alert(d.message || "Registration Successful!"); 
                        switchTab('login'); 
                    } else {
                        alert(d.detail || "Registration fail hua!");
                    }
                } catch(e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.innerText = "Register";
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
                        checkState();
                    } else {
                        alert(d.detail || "Login fail hua!");
                    }
                } catch(e) {
                    alert("Network error: " + e.message);
                } finally {
                    btn.innerText = "Login";
                    btn.disabled = false;
                }
            }

            function checkState(){
                if(localStorage.getItem('t')){
                    document.getElementById('authSection').classList.add('hidden');
                    document.getElementById('dashSection').classList.remove('hidden');
                    document.getElementById('logoutBtn').classList.remove('hidden');
                } else {
                    document.getElementById('authSection').classList.remove('hidden');
                    document.getElementById('dashSection').classList.add('hidden');
                    document.getElementById('logoutBtn').classList.add('hidden');
                }
            }

            function logout(){ localStorage.removeItem('t'); checkState(); }

            function previewImg(e){
                const file = e.target.files[0];
                if(file){
                    const r = new FileReader();
                    r.onload = function(ev){
                        document.getElementById('preview').src = ev.target.result;
                        document.getElementById('preview').classList.remove('hidden');
                        document.getElementById('uBox').classList.add('hidden');
                    }
                    r.readAsDataURL(file);
                }
            }

            async function analyzeChart(){
                const fi = document.getElementById('fileInput');
                const prompt = document.getElementById('promptInput').value;
                if(!fi.files[0]) return alert("Screenshot select karein!");

                const btn = document.getElementById('anBtn');
                btn.disabled = true;
                btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Analyzing 1M + 1W Data...`;

                const fd = new FormData();
                fd.append('file', fi.files[0]);
                fd.append('prompt', prompt);

                try {
                    const res = await fetch('/api/analyze', { method:'POST', body: fd });
                    const d = await res.json();
                    if(res.ok){
                        document.getElementById('resBox').classList.remove('hidden');
                        document.getElementById('resText').innerText = d.analysis;
                    } else alert(d.detail || "Error aaya!");
                } catch(e){ alert("Error: "+e.message); }
                finally {
                    btn.disabled = false;
                    btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> 1-Month + 1-Week Deep Prediction`;
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
