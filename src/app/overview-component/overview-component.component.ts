import { Component, inject, ViewChild, ElementRef, AfterViewInit, effect, OnDestroy, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { AtsScoringService } from '../services/ats-scoring.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-overview-component',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './overview-component.component.html',
  styleUrl: './overview-component.component.css'
})
export class OverviewComponentComponent implements AfterViewInit, OnDestroy, OnInit {
  scoringService = inject(AtsScoringService);
  platformId = inject(PLATFORM_ID);

  @ViewChild('scoreDistributionChart') scoreDistributionChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('topCandidatesChart') topCandidatesChartRef!: ElementRef<HTMLCanvasElement>;

  private distributionChartInstance: any = null;
  private topCandidatesChartInstance: any = null;

  constructor() {
    effect(() => {
      const candidates = this.scoringService.candidates();
      this.updateCharts(candidates);
    });
  }

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.scoringService.loadCandidates();
    }
  }

  get averageScore() {
    const list = this.scoringService.candidates();
    if (list.length === 0) return 0;
    const total = list.reduce((sum, c) => sum + c.score, 0);
    return Math.round(total / list.length);
  }

  get totalCandidates() {
    return this.scoringService.candidates().length;
  }

  ngAfterViewInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.initCharts().then(() => {
        this.updateCharts(this.scoringService.candidates());
      });
    }
  }

  ngOnDestroy() {
    if (this.distributionChartInstance) {
      this.distributionChartInstance.destroy();
    }
    if (this.topCandidatesChartInstance) {
      this.topCandidatesChartInstance.destroy();
    }
  }

  private async initCharts() {
    // Dynamic import to avoid SSR 'window is not defined' error
    const ChartModule = await import('chart.js/auto');
    const Chart = ChartModule.default;

    const distCtx = this.scoreDistributionChartRef?.nativeElement?.getContext('2d');
    if (distCtx) {
      this.distributionChartInstance = new Chart(distCtx, {
        type: 'doughnut',
        data: {
          labels: ['Sangat Baik (90-100)', 'Baik (75-89)', 'Cukup (60-74)', 'Kurang (<60)'],
          datasets: [{
            data: [0, 0, 0, 0],
            backgroundColor: [
              '#0d9488', // teal-600
              '#3b82f6', // blue-500
              '#eab308', // yellow-500
              '#ef4444'  // red-500
            ],
            borderWidth: 0,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                  family: "'Inter', sans-serif",
                  size: 12
                }
              }
            }
          },
          cutout: '70%'
        }
      });
    }

    const topCtx = this.topCandidatesChartRef?.nativeElement?.getContext('2d');
    if (topCtx) {
      this.topCandidatesChartInstance = new Chart(topCtx, {
        type: 'bar',
        data: {
          labels: [],
          datasets: [{
            label: 'Skor ATS',
            data: [],
            backgroundColor: '#0d9488', // teal-600
            borderRadius: 6,
            barThickness: 24
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: {
                display: true,
                color: '#f3f4f6' // gray-100
              },
              border: {
                display: false
              }
            },
            x: {
              grid: {
                display: false
              },
              border: {
                display: false
              }
            }
          }
        }
      });
    }
  }

  private updateCharts(candidates: any[]) {
    if (!this.distributionChartInstance || !this.topCandidatesChartInstance) return;

    let excellent = 0, good = 0, average = 0, poor = 0;
    candidates.forEach(c => {
      if (c.score >= 90) excellent++;
      else if (c.score >= 75) good++;
      else if (c.score >= 60) average++;
      else poor++;
    });

    this.distributionChartInstance.data.datasets[0].data = [excellent, good, average, poor];
    this.distributionChartInstance.update();

    const sorted = [...candidates].sort((a, b) => b.score - a.score).slice(0, 5);
    this.topCandidatesChartInstance.data.labels = sorted.map(c => c.name.split(' ')[0]);
    this.topCandidatesChartInstance.data.datasets[0].data = sorted.map(c => c.score);
    this.topCandidatesChartInstance.update();
  }
}
