from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import io
import os
import uuid
import sqlite3
import json
from pdfminer.high_level import extract_text
import re
import hashlib
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="ATS Parsing Backend with Auth")

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database Setup
DB_FILE = "ats.db"

# JWT Config
SECRET_KEY = "skripsweet_secret_key_2026_super_secure_32bytes"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 hari

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT,
            role TEXT,
            score INTEGER,
            skills TEXT,
            experience TEXT,
            education TEXT,
            file_path TEXT
        )
    ''')
    
    # Tabel User HRD
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    # Insert default admin jika belum ada
    c.execute("SELECT * FROM users WHERE email='admin@hrd.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", 
                  ("admin@hrd.com", hash_password("password123")))
                  
    conn.commit()
    conn.close()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === AUTHENTICATION LOGIC ===
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token tidak valid")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid atau sudah kedaluwarsa")

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email=?", (form_data.username,))
    row = c.fetchone()
    conn.close()
    
    if not row or row[0] != hash_password(form_data.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")
        
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

from typing import List, Optional

class UpdateProfileRequest(BaseModel):
    email: Optional[str] = None
    old_password: str
    new_password: Optional[str] = None

@app.put("/api/users/me")
def update_profile(req: UpdateProfileRequest, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Verifikasi password lama
    c.execute("SELECT password FROM users WHERE email=?", (current_user,))
    row = c.fetchone()
    
    if not row or row[0] != hash_password(req.old_password):
        conn.close()
        raise HTTPException(status_code=400, detail="Password lama salah")
        
    # Update email dan password baru jika diberikan
    new_email = req.email if req.email else current_user
    new_pass_hash = hash_password(req.new_password) if req.new_password else row[0]
    
    c.execute("UPDATE users SET email=?, password=? WHERE email=?", (new_email, new_pass_hash, current_user))
    conn.commit()
    conn.close()
    
    return {"message": "Profil berhasil diperbarui"}

# === ATS LOGIC ===

class CandidateResponse(BaseModel):
    id: str
    name: str
    role: str
    score: int
    skills: List[str]
    experience: str
    education: str

REQUIRED_SKILLS = [
    "angular", "typescript", "tailwind", "node", "javascript", "react", "html", "css", 
    "git", "api", "python", "java", "sql", "mysql", "postgresql", "mongodb", "docker", 
    "aws", "php", "laravel", "vue", "express", "rest", "linux"
]

def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    ignore_words = ["curriculum vitae", "cv", "resume", "profil", "profile", "data pribadi", "biodata"]
    for line in lines[:10]:
        if line.lower() not in ignore_words and len(line) > 2:
            clean_name = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            if 3 < len(clean_name) < 40:
                return clean_name.title()
    return "Unknown Candidate"

def extract_education(text: str) -> str:
    edu_patterns = [
        r"(Universitas\s+[A-Za-z\s]+)", r"(Institut\s+[A-Za-z\s]+)", r"(Politeknik\s+[A-Za-z\s]+)",
        r"(Sekolah Tinggi\s+[A-Za-z\s]+)", r"(S1\s+[A-Za-z\s]+)", r"(S2\s+[A-Za-z\s]+)",
        r"(Sarjana\s+[A-Za-z\s]+)", r"bachelor.*?of.*?(science|arts|engineering|technology|komputer)", 
        r"B\.?Sc\.?", r"Master.*?of", r"M\.?Sc\.?"
    ]
    found_educations = []
    for pattern in edu_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            edu_str = match.group(0).replace('\n', ' ').strip()
            if len(edu_str) < 60 and edu_str.title() not in found_educations:
                found_educations.append(edu_str.title())
    if found_educations:
        return " | ".join(found_educations[:2])
    return "Tidak Ditemukan / Belum Lulus"

def extract_experience_section(text: str) -> str:
    lines = text.split('\n')
    experience_headers = ["pengalaman", "pengalaman kerja", "riwayat pekerjaan", "experience", "work experience", "working experience", "working experiences", "organisasi", "riwayat kerja"]
    other_headers = ["pendidikan", "education", "skill", "keterampilan", "keahlian", "sertifikasi", "project", "referensi", "kontak", "hobi", "kemampuan", "skills"]
    in_experience_section = False
    extracted_text = []
    for line in lines:
        clean_line = line.strip().lower()
        clean_line = re.sub(r'^[^a-z0-9]+', '', clean_line).strip()
        if (clean_line in experience_headers or any(clean_line.startswith(h) for h in experience_headers)) and len(clean_line) < 40:
            in_experience_section = True
            continue
        if in_experience_section:
            if (clean_line in other_headers or any(clean_line.startswith(h) for h in other_headers)) and len(clean_line) < 40:
                break
            if line.strip():
                extracted_text.append(line.strip())
    if extracted_text:
        result = " ".join(extracted_text)
        return result[:400] + "..." if len(result) > 400 else result
    return "Detail pengalaman tidak ditemukan. Harap pastikan CV memiliki subjudul seperti 'Pengalaman Kerja' atau 'Working Experiences'."

def calculate_ats_score(text: str) -> tuple[int, List[str]]:
    text_lower = text.lower()
    matched_skills = set()
    for skill in REQUIRED_SKILLS:
        if skill in ["c++", "c#"]:
            if skill in text_lower:
                matched_skills.add(skill.capitalize())
        elif re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            matched_skills.add(skill.capitalize())
    matched_list = list(matched_skills)
    max_expected_skills = 8 
    score = int((len(matched_list) / max_expected_skills) * 100)
    score = min(score, 100)
    score = max(score, 30) 
    if len(matched_list) == 0:
        matched_list = ["Microsoft Office"]
    return score, matched_list

@app.get("/")
def read_root():
    return {"message": "ATS Backend is running. Auth Enabled."}

# TAMBAHKAN user: str = Depends(get_current_user) UNTUK MEMPROTEKSI ENDPOINT
@app.post("/api/parse-cv", response_model=CandidateResponse)
async def parse_cv(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung")
    try:
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.pdf"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            
        pdf_file = io.BytesIO(contents)
        raw_text = extract_text(pdf_file)
        
        name = extract_name(raw_text)
        if name == "Unknown Candidate":
            name = file.filename.replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
            
        education = extract_education(raw_text)
        experience = extract_experience_section(raw_text)
        score, skills = calculate_ats_score(raw_text)
        
        role = "Software Engineer"
        if "Php" in skills or "Laravel" in skills or "Node" in skills:
            role = "Backend Developer"
        elif "React" in skills or "Angular" in skills or "Vue" in skills:
            role = "Frontend Developer"
            
        skills_json = json.dumps(skills[:10])
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO candidates (id, name, role, score, skills, experience, education, file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (file_id, name, role, score, skills_json, experience, education, file_path)
        )
        conn.commit()
        conn.close()
        
        return CandidateResponse(
            id=file_id,
            name=name,
            role=role,
            score=score,
            skills=skills[:10],
            experience=experience,
            education=education
        )
    except Exception as e:
        print("Error parsing:", str(e))
        raise HTTPException(status_code=500, detail="Gagal memproses file.")

@app.get("/api/candidates", response_model=List[CandidateResponse])
def get_candidates(current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, role, score, skills, experience, education FROM candidates ORDER BY rowid DESC")
    rows = c.fetchall()
    conn.close()
    
    candidates = []
    for row in rows:
        candidates.append(CandidateResponse(
            id=row[0],
            name=row[1],
            role=row[2],
            score=row[3],
            skills=json.loads(row[4]),
            experience=row[5],
            education=row[6]
        ))
    return candidates

@app.delete("/api/candidates/{candidate_id}")
def delete_candidate(candidate_id: str, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT file_path FROM candidates WHERE id = ?", (candidate_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    file_path = row[0]
    
    c.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return {"message": "Candidate deleted successfully"}

@app.get("/api/download/{candidate_id}")
def download_cv(candidate_id: str, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT file_path, name FROM candidates WHERE id = ?", (candidate_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    file_path, name = row
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on server")
        
    clean_name = name.replace(" ", "_")
    return FileResponse(path=file_path, filename=f"CV_{clean_name}.pdf", media_type='application/pdf')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
