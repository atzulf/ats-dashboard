import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-settings-component',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings-component.component.html',
  styleUrl: './settings-component.component.css'
})
export class SettingsComponentComponent {
  email = '';
  oldPassword = '';
  newPassword = '';
  
  message = signal<{text: string, type: 'error' | 'success'} | null>(null);
  isLoading = signal<boolean>(false);
  
  private authService = inject(AuthService);

  async onUpdate() {
    if (!this.oldPassword) {
      this.message.set({text: 'Password Lama wajib diisi untuk verifikasi keamanan!', type: 'error'});
      return;
    }

    if (!this.email && !this.newPassword) {
      this.message.set({text: 'Harap isi minimal Email Baru atau Password Baru.', type: 'error'});
      return;
    }
    
    this.isLoading.set(true);
    this.message.set(null);
    
    const result = await this.authService.updateProfile(this.oldPassword, this.email, this.newPassword);
    
    this.message.set({
      text: result.message,
      type: result.success ? 'success' : 'error'
    });
    
    this.isLoading.set(false);
  }
}
