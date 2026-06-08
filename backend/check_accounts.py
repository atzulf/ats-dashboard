import sqlite3
import hashlib
import os

DB_FILE = "ats.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_accounts():
    if not os.path.exists(DB_FILE):
        print("Database belum dibuat. Jalankan server backend terlebih dahulu.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, email FROM users")
    rows = c.fetchall()
    
    print("\n" + "="*40)
    print("📋 DAFTAR AKUN HRD DI DATABASE ATS")
    print("="*40)
    
    if not rows:
        print("Tidak ada akun yang ditemukan.")
    else:
        for row in rows:
            print(f"ID     : {row[0]}")
            print(f"Email  : {row[1]}")
            print("-" * 40)
            
    print("\n💡 TIPS: Jika Anda lupa password, jalankan fungsi reset di bawah.")
    
    reset = input("Apakah Anda ingin mereset akun pertama kembali menjadi admin@hrd.com / password123? (y/n): ")
    if reset.lower() == 'y':
        if rows:
            user_id = rows[0][0]
            c.execute("UPDATE users SET email=?, password=? WHERE id=?", 
                      ("admin@hrd.com", hash_password("password123"), user_id))
            conn.commit()
            print("✅ Berhasil! Akun telah di-reset ke admin@hrd.com / password123")
        else:
            print("❌ Gagal. Tidak ada akun untuk di-reset.")
            
    conn.close()

if __name__ == '__main__':
    check_accounts()
