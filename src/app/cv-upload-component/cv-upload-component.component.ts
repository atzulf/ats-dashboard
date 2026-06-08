import { Component, inject } from '@angular/core';
import { CvUploadService } from '../services/cv-upload.service';
import { AtsScoringService } from '../services/ats-scoring.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-cv-upload-component',
  standalone: true,
  imports: [],
  templateUrl: './cv-upload-component.component.html',
  styleUrl: './cv-upload-component.component.css'
})
export class CvUploadComponentComponent {
  uploadService = inject(CvUploadService);
  scoringService = inject(AtsScoringService);
  router = inject(Router);

  isDragging = false;
  showSuccess = false;

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  async onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      await this.handleUpload(files[0]);
    }
  }

  async onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      await this.handleUpload(input.files[0]);
    }
  }

  private async handleUpload(file: File) {
    this.showSuccess = false;
    try {
      const parsedData = await this.uploadService.uploadFile(file);
      this.scoringService.addCandidate(parsedData);
      this.showSuccess = true;
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        this.showSuccess = false;
        // Optionally navigate to candidates list
        this.router.navigate(['/candidates']);
      }, 3000);
    } catch (error) {
      console.error('Upload failed', error);
    }
  }
}
