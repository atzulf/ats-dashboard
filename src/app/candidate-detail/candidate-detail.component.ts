import { Component, input, output } from '@angular/core';
import { Candidate } from '../services/ats-scoring.service';
import { CommonModule } from '@angular/common';

const PRODUCTION_API_BASE_URL = 'https://backend-angular-ats.vercel.app';

function apiUrl(path: string): string {
  const baseUrl = typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')
    ? '/api'
    : PRODUCTION_API_BASE_URL;

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

@Component({
  selector: 'app-candidate-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './candidate-detail.component.html',
  styleUrl: './candidate-detail.component.css'
})
export class CandidateDetailComponent {
  // Angular 18 Signal Inputs
  candidate = input.required<Candidate>();
  downloadUrl = () => apiUrl(`/download/${this.candidate().id}`);
  
  // Angular 18 Signal Output
  closeModal = output<void>();
  deleteCandidate = output<string>();

  onClose() {
    this.closeModal.emit();
  }

  onDelete() {
    this.deleteCandidate.emit(this.candidate().id);
  }
}
