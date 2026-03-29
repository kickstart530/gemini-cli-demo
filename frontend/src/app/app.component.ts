import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';

import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, MatToolbarModule, MatButtonModule, MatIconModule, MatMenuModule],
  template: `
    <mat-toolbar color="primary">
      <button mat-icon-button routerLink="/events">
        <mat-icon>event</mat-icon>
      </button>
      <span routerLink="/events" style="cursor:pointer">Event Management</span>

      <span class="spacer"></span>

      <button mat-button routerLink="/events">Events</button>

      <ng-container *ngIf="auth.isLoggedIn()">
        <button mat-button routerLink="/events/create">Create Event</button>
        <button mat-button routerLink="/my-tickets">My Tickets</button>
        <button mat-icon-button [matMenuTriggerFor]="userMenu">
          <mat-icon>account_circle</mat-icon>
        </button>
        <mat-menu #userMenu="matMenu">
          <div style="padding: 8px 16px; font-weight: 500">{{ auth.currentUser()?.name }}</div>
          <button mat-menu-item (click)="auth.logout()">
            <mat-icon>logout</mat-icon>
            <span>Logout</span>
          </button>
        </mat-menu>
      </ng-container>

      <ng-container *ngIf="!auth.isLoggedIn()">
        <button mat-button routerLink="/login">Login</button>
        <button mat-raised-button color="accent" routerLink="/register">Register</button>
      </ng-container>
    </mat-toolbar>

    <main class="container">
      <router-outlet></router-outlet>
    </main>
  `,
})
export class AppComponent {
  constructor(public auth: AuthService, private router: Router) {}
}
