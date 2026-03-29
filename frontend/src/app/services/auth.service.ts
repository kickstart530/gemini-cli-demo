import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs';

import { environment } from '@env/environment';
import { User, Token } from '../models/interfaces';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private userSignal = signal<User | null>(null);
  currentUser = this.userSignal.asReadonly();
  isLoggedIn = computed(() => !!this.userSignal());

  constructor(private http: HttpClient, private router: Router) {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.loadProfile();
    }
  }

  register(data: { email: string; name: string; password: string; role?: string }) {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, data);
  }

  login(email: string, password: string) {
    return this.http.post<Token>(`${environment.apiUrl}/auth/login`, { email, password }).pipe(
      tap(token => {
        localStorage.setItem('access_token', token.access_token);
        this.loadProfile();
      }),
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    this.userSignal.set(null);
    this.router.navigate(['/login']);
  }

  private loadProfile() {
    this.http.get<User>(`${environment.apiUrl}/auth/me`).subscribe({
      next: user => this.userSignal.set(user),
      error: () => {
        localStorage.removeItem('access_token');
        this.userSignal.set(null);
      },
    });
  }
}
