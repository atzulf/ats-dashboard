import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface Candidate {
  id: string;
  name: string;
  role: string;
  score: number;
  skills: string[];
  experience: string;
  education: string;
}

@Injectable({
  providedIn: 'root'
})
export class AtsScoringService {
  private http = inject(HttpClient);
  candidates = signal<Candidate[]>([]);

  constructor() {
    this.loadCandidates();
  }

  async loadCandidates() {
    try {
      const data = await firstValueFrom(this.http.get<Candidate[]>('http://localhost:8000/api/candidates'));
      this.candidates.set(data);
    } catch (error) {
      console.error('Gagal mengambil data kandidat dari database', error);
    }
  }

  addCandidate(candidate: Candidate) {
    // Tambahkan data baru ke baris paling atas
    this.candidates.update(list => [candidate, ...list]);
  }

  async deleteCandidate(id: string) {
    try {
      // Hapus dari Database backend
      await firstValueFrom(this.http.delete(`http://localhost:8000/api/candidates/${id}`));
      // Hapus dari state UI lokal
      this.candidates.update(list => list.filter(c => c.id !== id));
    } catch (error) {
      console.error('Gagal menghapus kandidat', error);
      alert("Gagal menghapus kandidat. Pastikan server berjalan.");
    }
  }
}
