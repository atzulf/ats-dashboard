import { Component, input, output } from '@angular/core';
import { Candidate } from '../services/ats-scoring.service';
import { CommonModule } from '@angular/common';

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
