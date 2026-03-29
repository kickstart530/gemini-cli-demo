import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { EventService } from '../../services/event.service';
import { EventAnalytics } from '../../models/interfaces';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [
    CommonModule, RouterModule,
    MatCardModule, MatButtonModule, MatIconModule, MatProgressBarModule,
  ],
  template: `
    <div *ngIf="analytics">
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
        <button mat-icon-button [routerLink]="['/events', analytics.event_id]">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Analytics: {{ analytics.event_title }}</h1>
      </div>

      <div class="dashboard-cards">
        <mat-card class="stat-card">
          <div class="stat-value">{{ analytics.total_registrations }}</div>
          <div class="stat-label">Registrations</div>
          <mat-progress-bar mode="determinate"
            [value]="(analytics.total_registrations / analytics.total_capacity) * 100"
            style="margin-top:12px">
          </mat-progress-bar>
          <div style="color:#666;font-size:0.8rem;margin-top:4px">
            {{ analytics.total_registrations }} / {{ analytics.total_capacity }} capacity
          </div>
        </mat-card>

        <mat-card class="stat-card">
          <div class="stat-value">{{ analytics.total_checked_in }}</div>
          <div class="stat-label">Checked In</div>
          <div style="color:#666;margin-top:8px">{{ analytics.check_in_rate }}% check-in rate</div>
        </mat-card>

        <mat-card class="stat-card">
          <div class="stat-value">\${{ analytics.total_revenue.toFixed(2) }}</div>
          <div class="stat-label">Total Revenue</div>
        </mat-card>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
        <mat-card>
          <mat-card-header><mat-card-title>Tickets by Type</mat-card-title></mat-card-header>
          <mat-card-content>
            <div *ngFor="let tt of analytics.tickets_by_type" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee">
              <span>{{ tt.type }}</span>
              <span>{{ tt.count }} sold - \${{ tt.revenue.toFixed(2) }}</span>
            </div>
            <p *ngIf="analytics.tickets_by_type.length === 0" style="color:#666">No ticket data yet.</p>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header><mat-card-title>Registrations Over Time</mat-card-title></mat-card-header>
          <mat-card-content>
            <div *ngFor="let r of analytics.registrations_over_time" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee">
              <span>{{ r.date }}</span>
              <span>{{ r.count }} registrations</span>
            </div>
            <p *ngIf="analytics.registrations_over_time.length === 0" style="color:#666">No registration data yet.</p>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
})
export class AnalyticsComponent implements OnInit {
  analytics: EventAnalytics | null = null;

  constructor(private route: ActivatedRoute, private eventService: EventService) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.eventService.getAnalytics(id).subscribe(data => this.analytics = data);
  }
}
