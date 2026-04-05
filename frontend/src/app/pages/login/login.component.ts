import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterModule,
    MatCardModule, MatButtonModule, MatInputModule, MatFormFieldModule, MatSnackBarModule,
  ],
  template: `
    <div style="max-width:400px;margin:48px auto">
      <mat-card>
        <mat-card-header><mat-card-title>Login</mat-card-title></mat-card-header>
        <mat-card-content>
          <form (ngSubmit)="onLogin()" style="display:flex;flex-direction:column;gap:16px;margin-top:16px">
            <mat-form-field appearance="outline">
              <mat-label>Email</mat-label>
              <input matInput type="email" [(ngModel)]="email" name="email" required>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>Password</mat-label>
              <input matInput type="password" [(ngModel)]="password" name="password" required>
            </mat-form-field>
            <button mat-raised-button color="primary" type="submit">Login</button>
          </form>
          <p style="text-align:center;margin-top:16px">
            Don't have an account? <a routerLink="/register">Register</a>
          </p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
})
export class LoginComponent {
  email = '';
  password = '';

  constructor(private auth: AuthService, private router: Router, private snackBar: MatSnackBar) {}

  onLogin() {
    this.auth.login(this.email, this.password).subscribe({
      next: () => this.router.navigate(['/events']),
      error: () => this.snackBar.open('Invalid credentials', 'Close', { duration: 3000 }),
    });
  }
}
