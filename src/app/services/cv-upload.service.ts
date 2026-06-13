import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CvUploadService {
  private http = inject(HttpClient);
  
  uploadProgress = signal<number>(0);
  isUploading = signal<boolean>(false);

  async uploadFile(file: File): Promise<any> {
    this.isUploading.set(true);
    this.uploadProgress.set(20);

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      this.uploadProgress.set(60);

      // Call the FastAPI backend
      const response = await firstValueFrom(
        this.http.post('https://backend-angular-ats.vercel.app/api/parse-cv', formData)
      );

      this.uploadProgress.set(100);
      
      // Artificial delay so the user sees the 100% completion bar
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return response;
    } catch (error) {
      console.error('Error uploading file to backend:', error);
      throw error;
    } finally {
      this.isUploading.set(false);
    }
  }
}
