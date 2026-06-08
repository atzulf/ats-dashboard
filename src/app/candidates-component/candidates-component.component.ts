import { Component, inject, signal } from '@angular/core';
import { AtsScoringService, Candidate } from '../services/ats-scoring.service';
import { CommonModule } from '@angular/common';
import { CandidateDetailComponent } from '../candidate-detail/candidate-detail.component';

@Component({
  selector: 'app-candidates-component',
  standalone: true,
  imports: [CommonModule, CandidateDetailComponent],
  templateUrl: './candidates-component.component.html',
  styleUrl: './candidates-component.component.css'
})
export class CandidatesComponentComponent {
  scoringService = inject(AtsScoringService);
  selectedCandidate = signal<Candidate | null>(null);

  viewDetails(candidate: Candidate) {
    this.selectedCandidate.set(candidate);
  }

  closeDetails() {
    this.selectedCandidate.set(null);
  }

  onDeleteCandidate(id: string) {
    this.scoringService.deleteCandidate(id);
    this.selectedCandidate.set(null);
  }
}
