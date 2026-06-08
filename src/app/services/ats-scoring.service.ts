import { Injectable, signal } from '@angular/core';

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
  candidates = signal<Candidate[]>([]);
  
  addCandidate(candidate: Omit<Candidate, 'id'>) {
    const newCandidate = {
      ...candidate,
      id: Math.random().toString(36).substring(2, 9)
    };
    this.candidates.update(list => [...list, newCandidate]);
  }

  deleteCandidate(id: string) {
    this.candidates.update(list => list.filter(c => c.id !== id));
  }
}
