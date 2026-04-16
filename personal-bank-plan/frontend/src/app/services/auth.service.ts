import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs';

const API = 'http://localhost:8000/api';

interface LoginResponse {
  token: string;
  user: { id: number; username: string };
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  isAuthenticated = signal(!!localStorage.getItem('auth_token'));

  login(username: string, password: string) {
    return this.http.post<LoginResponse>(`${API}/auth/login/`, { username, password }).pipe(
      tap((res) => {
        localStorage.setItem('auth_token', res.token);
        this.isAuthenticated.set(true);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    this.isAuthenticated.set(false);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}
