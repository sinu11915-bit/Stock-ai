import os
import io
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from jose import jwt
from PIL import Image
from pydantic import BaseModel

app = FastAPI(title="NiftyLens AI")

SECRET_KEY = "my_super_secret_trading_jwt_key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    conn = sqlite3.connect("database.db")
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
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    hashed = pwd_context.hash(data.password)
    try:
        c.execute("INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
                  (data.email.strip().lower(), data.phone.strip(), hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email ya Phone pehle se registered hai!")
    conn.close()
    return {"message": "Registration successful! Ab login karein."}

@app.post("/api/login")
def login(data: LoginData):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT email, password FROM users WHERE email=? OR phone=?", 
              (data.identifier.strip().lower(), data.identifier.strip()))
    user = c.fetchone()
    conn.close()
    if not user or not pwd_context.verify(data.password, user[1]):
        raise HTTPException(status_code=400, detail="Galat Email/Phone ya Password!")
    
    token = jwt.encode({"sub": user[0]}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "email": user[0]}

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
        image = Image.open(io.BytesIO(image_bytes))

        system_prompt = f"""
        Aap ek professional Technical Chart Analyst hain Indian Stock Market (NSE/BSE/Nifty) ke liye.
        User sawal: {prompt if prompt else 'Is chart ka analysis karke Entry, SL aur Target batao.'}

        Chart ke right side Y-axis par jo ASLI PRICE dikh rahi hai sirf wahi price read karein aur response de:
        1. SYMBOL & TIMEFRAME: (Stock/Index ka naam aur timeframe)
        2. TREND: (Bullish / Bearish / Sideways)
        3. KEY SUPPORT & RESISTANCE: (Y-axis ke hisab se exact numbers)
        4. BUY SETUP: (Entry level, Stop-Loss, Target 1 aur Target 2)
        5. SELL/PUT SETUP: (Breakdown entry, Stop-Loss, Target)
        6. REASONING & DISCLAIMER: (Kyu yeh trade ban raha hai)
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[system_prompt, image]
        )
        return {"analysis": response.text}

    except Exception:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[system_prompt, image]
            )
            return {"analysis": response.text}
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"AI Error: {str(err)}")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NiftyLens AI Analyst</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
        <div class="max-w-md mx-auto p-4 min-h-screen flex flex-col justify-between">
            <div class="flex justify-between items-center py-3 border-b border-slate-800">
                <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-chart-pie text-emerald-400 text-2xl"></i>
                    <h1 class="text-xl font-bold tracking-wider">NiftyLens AI</h1>
                </div>
                <button id="logoutBtn" onclick="logout()" class="hidden text-xs bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg">Logout</button>
            </div>

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
                        <button onclick="loginUser()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3 rounded-xl">Login</button>
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
                        <button onclick="registerUser()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3 rounded-xl">Register</button>
                    </div>
                </div>
            </div>

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
                    <label class="text-xs text-slate-400">Aapka Sawal / Prompt</label>
                    <input id="promptInput" type="text" class="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 mt-1 text-sm text-white" placeholder="e.g. Abhi Buy karein ya Sell? Target aur Stop Loss kya hoga?">
                </div>

                <button id="anBtn" onclick="analyzeChart()" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold py-3.5 rounded-xl shadow-lg transition">
                    <i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Analyze Chart
                </button>

                <div id="resBox" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-4 mt-2">
                    <h3 class="text-sm font-bold text-emerald-400 border-b border-slate-800 pb-2 flex items-center">
                        <i class="fa-solid fa-bolt mr-2"></i> Real AI Technical Prediction
                    </h3>
                    <div id="resText" class="mt-3 text-xs leading-relaxed text-slate-200 whitespace-pre-wrap"></div>
                </div>
            </div>

            <div class="text-center py-2 text-[10px] text-slate-600">
                NiftyLens AI &bull; For Technical & Educational Use Only
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

                const res = await fetch('/api/register', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({email, phone, password})
                });
                const d = await res.json();
                if(res.ok){ alert(d.message); switchTab('login'); }
                else alert(d.detail);
            }

            async function loginUser(){
                const identifier = document.getElementById('lId').value;
                const password = document.getElementById('lPass').value;
                if(!identifier || !password) return alert("Email/Phone aur Password bharein!");

                const res = await fetch('/api/login', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({identifier, password})
                });
                const d = await res.json();
                if(res.ok){
                    localStorage.setItem('t', d.token);
                    checkState();
                } else alert(d.detail);
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
                btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Analyzing Chart...`;

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
                    btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Analyze Chart`;
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
