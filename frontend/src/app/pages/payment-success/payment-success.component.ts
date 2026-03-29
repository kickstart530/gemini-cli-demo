import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-payment-success',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule],
  template: `
    <div style="max-width:500px;margin:48px auto;text-align:center">
      <mat-card>
        <mat-card-content>
          <mat-icon style="font-size:64px;width:64px;height:64px;color:#4caf50">check_circle</mat-icon>
          <h2 style="margin-top:16px">Payment Successful!</h2>
          <p style="color:#666;margin-top:8px">Your ticket has been purchased successfully.</p>
          <div style="margin-top:24px;display:flex;gap:16px;justify-content:center">
            <button mat-raised-button color="primary" routerLink="/my-tickets">View My Tickets</button>
            <button mat-button routerLink="/events">Browse Events</button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
})
export class PaymentSuccessComponent {}
