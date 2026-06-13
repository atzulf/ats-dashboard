import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login-component',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login-component.component.html',
  styleUrl: './login-component.component.css'
})
export class LoginComponentComponent {
  email = '';
  password = '';
  errorMsg = signal<string>('');
  isLoading = signal<boolean>(false);
  
  private authService = inject(AuthService);

  async onLogin() {
    if (!this.email || !this.password) {
      this.errorMsg.set('Harap isi email dan password');
      return;
    }
    
    this.isLoading.set(true);
    this.errorMsg.set('');
    
    const result = await this.authService.login(this.email, this.password);

    if (!result.success) {
      this.errorMsg.set(result.message);
    }
    
    this.isLoading.set(false);
  }
}
