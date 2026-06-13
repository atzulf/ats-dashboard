import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  
  isAuthenticated = signal<boolean>(false);

  constructor() {
    // Cek apakah ada token di localStorage saat aplikasi dimuat
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      this.isAuthenticated.set(!!token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  async login(email: string, password: string): Promise<boolean> {
    try {
      const formData = new URLSearchParams();
      formData.set('username', email);
      formData.set('password', password);

      const res: any = await firstValueFrom(this.http.post('https://backend-angular-ats.vercel.app/api/login', formData.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }));
      
      localStorage.setItem('access_token', res.access_token);
      this.isAuthenticated.set(true);
      this.router.navigate(['/']);
      return true;
    } catch (error) {
      console.error('Login failed', error);
      return false;
    }
  }

  async updateProfile(oldPass: string, email?: string, newPass?: string): Promise<{success: boolean, message: string}> {
    try {
      const payload: any = { old_password: oldPass };
      if (email) payload.email = email;
      if (newPass) payload.new_password = newPass;

      const res: any = await firstValueFrom(this.http.put('https://backend-angular-ats.vercel.app/api/users/me', payload));
      
      // Paksa logout agar sesi ter-refresh
      this.logout();
      
      return { success: true, message: 'Berhasil! Silakan login ulang dengan kredensial baru.' };
    } catch (error: any) {
      console.error('Update failed', error);
      return { 
        success: false, 
        message: error.error?.detail || 'Gagal mengubah profil' 
      };
    }
  }

  logout() {
    localStorage.removeItem('access_token');
    this.isAuthenticated.set(false);
    this.router.navigate(['/login']);
  }
}
