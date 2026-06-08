import { Component, inject } from '@angular/core';
import { AtsScoringService } from '../services/ats-scoring.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-overview-component',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './overview-component.component.html',
  styleUrl: './overview-component.component.css'
})
export class OverviewComponentComponent {
  scoringService = inject(AtsScoringService);

  get averageScore() {
    const list = this.scoringService.candidates();
    if (list.length === 0) return 0;
    const total = list.reduce((sum, c) => sum + c.score, 0);
    return Math.round(total / list.length);
  }

  get totalCandidates() {
    return this.scoringService.candidates().length;
  }
}
