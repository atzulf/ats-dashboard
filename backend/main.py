from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import io
from pdfminer.high_level import extract_text
import re

app = FastAPI(title="ATS Parsing Backend")

@app.get("/")
def read_root():
    return {"message": "ATS Backend is running. Please use the Angular UI to upload CVs."}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParsedCV(BaseModel):
    name: str
    role: str
    score: int
    skills: List[str]
    experience: str
    education: str

# Expanded Skill List
REQUIRED_SKILLS = [
    "angular", "typescript", "tailwind", "node", "javascript", "react", "html", "css", 
    "git", "api", "python", "java", "sql", "mysql", "postgresql", "mongodb", "docker", 
    "aws", "php", "laravel", "vue", "express", "rest", "linux"
]

def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    ignore_words = ["curriculum vitae", "cv", "resume", "profil", "profile", "data pribadi", "biodata"]
    
    for line in lines[:10]:
        # Jika baris ini bukan kata-kata umum seperti "Curriculum Vitae"
        if line.lower() not in ignore_words and len(line) > 2:
            # Ambil hanya huruf dan spasi, hapus angka/simbol aneh
            clean_name = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            # Pastikan nama tidak terlalu panjang (bukan kalimat) dan bukan single word singkatan
            if 3 < len(clean_name) < 40:
                return clean_name.title()
    return "Unknown Candidate"

def extract_education(text: str) -> str:
    # Regex untuk bahasa Indonesia dan Inggris
    edu_patterns = [
        r"(Universitas\s+[A-Za-z\s]+)",
        r"(Institut\s+[A-Za-z\s]+)",
        r"(Politeknik\s+[A-Za-z\s]+)",
        r"(Sekolah Tinggi\s+[A-Za-z\s]+)",
        r"(S1\s+[A-Za-z\s]+)",
        r"(S2\s+[A-Za-z\s]+)",
        r"(Sarjana\s+[A-Za-z\s]+)",
        r"bachelor.*?of.*?(science|arts|engineering|technology|komputer)", 
        r"B\.?Sc\.?", 
        r"Master.*?of", 
        r"M\.?Sc\.?"
    ]
    
    found_educations = []
    for pattern in edu_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Bersihkan newline
            edu_str = match.group(0).replace('\n', ' ').strip()
            # Hindari duplikat atau string terlalu panjang (mengindari false positive)
            if len(edu_str) < 60 and edu_str.title() not in found_educations:
                found_educations.append(edu_str.title())
                
    if found_educations:
        return " | ".join(found_educations[:2]) # Ambil max 2 riwayat pendidikan
    return "Tidak Ditemukan / Belum Lulus"

def extract_experience_section(text: str) -> str:
    lines = text.split('\n')
    experience_headers = ["pengalaman", "pengalaman kerja", "riwayat pekerjaan", "experience", "work experience", "working experience", "working experiences", "organisasi", "riwayat kerja"]
    other_headers = ["pendidikan", "education", "skill", "keterampilan", "keahlian", "sertifikasi", "project", "referensi", "kontak", "hobi", "kemampuan", "skills"]
    
    in_experience_section = False
    extracted_text = []
    
    for line in lines:
        clean_line = line.strip().lower()
        # Bersihkan simbol/karakter aneh di awal baris yang mungkin dibaca oleh parser
        clean_line = re.sub(r'^[^a-z0-9]+', '', clean_line).strip()
        
        # Cek apakah ini merupakan header pengalaman (panjang baris pendek = header)
        if (clean_line in experience_headers or any(clean_line.startswith(h) for h in experience_headers)) and len(clean_line) < 40:
            in_experience_section = True
            continue
            
        if in_experience_section:
            # Cek apakah sudah menabrak header bagian lain (Pendidikan, Skill, dll)
            if (clean_line in other_headers or any(clean_line.startswith(h) for h in other_headers)) and len(clean_line) < 40:
                break
                
            if line.strip():
                extracted_text.append(line.strip())
            
    if extracted_text:
        result = " ".join(extracted_text)
        # Batasi output maksimal 400 karakter agar UI panel tidak kepenuhan
        return result[:400] + "..." if len(result) > 400 else result
        
    return "Detail pengalaman tidak ditemukan. Harap pastikan CV memiliki subjudul seperti 'Pengalaman Kerja' atau 'Working Experiences'."

def calculate_ats_score(text: str) -> tuple[int, List[str]]:
    text_lower = text.lower()
    matched_skills = set() # Gunakan set agar tidak ada duplikat
    
    # Deteksi spesifik (menggunakan regex bounds agar tidak false positive seperti 'css' cocok dengan 'access')
    for skill in REQUIRED_SKILLS:
        # Pengecualian untuk C++ atau C# yang susah di-regex boundary
        if skill in ["c++", "c#"]:
            if skill in text_lower:
                matched_skills.add(skill.capitalize())
        elif re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            matched_skills.add(skill.capitalize())
            
    matched_list = list(matched_skills)
    
    # Hitung persentase (asumsi 8 skill adalah target ideal untuk mendapat 100%)
    max_expected_skills = 8 
    score = int((len(matched_list) / max_expected_skills) * 100)
    
    # Batasi max 100
    score = min(score, 100)
    
    # Berikan base score 30 agar tidak 0
    score = max(score, 30) 
    
    if len(matched_list) == 0:
        matched_list = ["Microsoft Office"]
        
    return score, matched_list

@app.post("/api/parse-cv", response_model=ParsedCV)
async def parse_cv(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung saat ini")
        
    try:
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        raw_text = extract_text(pdf_file)
        
        # 1. Ekstrak Nama
        name = extract_name(raw_text)
        if name == "Unknown Candidate":
            name = file.filename.replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
            
        # 2. Ekstrak Pendidikan
        education = extract_education(raw_text)
        
        # 3. Ekstrak Pengalaman
        experience = extract_experience_section(raw_text)
        
        # 4. Hitung Skor ATS & Skills
        score, skills = calculate_ats_score(raw_text)
        
        # 5. Tebak Role secara Dinamis
        role = "Software Engineer"
        if "Php" in skills or "Laravel" in skills or "Node" in skills:
            role = "Backend Developer"
        elif "React" in skills or "Angular" in skills or "Vue" in skills:
            role = "Frontend Developer"
            
        return ParsedCV(
            name=name,
            role=role,
            score=score,
            skills=skills[:10], # Max 10 skills di UI
            experience=experience,
            education=education
        )
        
    except Exception as e:
        print("Error parsing:", str(e))
        raise HTTPException(status_code=500, detail="Gagal memproses file. Pastikan PDF berupa teks, bukan gambar hasil scan.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
