import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterModule,
    MatCardModule, MatButtonModule, MatInputModule, MatFormFieldModule, MatSelectModule, MatSnackBarModule,
  ],
  template: `
    <div style="max-width:400px;margin:48px auto">
      <mat-card>
        <mat-card-header><mat-card-title>Register</mat-card-title></mat-card-header>
        <mat-card-content>
          <form (ngSubmit)="onRegister()" style="display:flex;flex-direction:column;gap:16px;margin-top:16px">
            <mat-form-field appearance="outline">
              <mat-label>Name</mat-label>
              <input matInput [(ngModel)]="name" name="name" required>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>Email</mat-label>
              <input matInput type="email" [(ngModel)]="email" name="email" required>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>Password</mat-label>
              <input matInput type="password" [(ngModel)]="password" name="password" required>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>Role</mat-label>
              <mat-select [(ngModel)]="role" name="role">
                <mat-option value="attendee">Attendee</mat-option>
                <mat-option value="organizer">Organizer</mat-option>
              </mat-select>
            </mat-form-field>
            <button mat-raised-button color="primary" type="submit">Register</button>
          </form>
          <p style="text-align:center;margin-top:16px">
            Already have an account? <a routerLink="/login">Login</a>
          </p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
})
export class RegisterComponent {
  name = '';
  email = '';
  password = '';
  role = 'attendee';

  constructor(private auth: AuthService, private router: Router, private snackBar: MatSnackBar) {}

  onRegister() {
    this.auth.register({ name: this.name, email: this.email, password: this.password, role: this.role }).subscribe({
      next: () => {
        this.snackBar.open('Registration successful! Please login.', 'Close', { duration: 3000 });
        this.router.navigate(['/login']);
      },
      error: err => this.snackBar.open(err.error?.detail || 'Registration failed', 'Close', { duration: 3000 }),
    });
  }
}
