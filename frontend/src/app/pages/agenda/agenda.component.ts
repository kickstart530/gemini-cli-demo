import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';

import { EventService } from '../../services/event.service';
import { Session, Event } from '../../models/interfaces';

@Component({
  selector: 'app-agenda',
  standalone: true,
  imports: [
    CommonModule, RouterModule,
    MatCardModule, MatButtonModule, MatIconModule, MatChipsModule,
  ],
  template: `
    <div *ngIf="event">
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
        <button mat-icon-button [routerLink]="['/events', event.id]">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Agenda: {{ event.title }}</h1>
      </div>

      <div style="margin-bottom:16px">
        <mat-chip-listbox>
          <mat-chip-option *ngFor="let track of tracks"
            [selected]="selectedTrack === track"
            (click)="filterByTrack(track)">
            {{ track }}
          </mat-chip-option>
          <mat-chip-option [selected]="!selectedTrack" (click)="filterByTrack(null)">All Tracks</mat-chip-option>
        </mat-chip-listbox>
      </div>

      <div class="card-grid">
        <mat-card *ngFor="let session of filteredSessions" style="border-left:4px solid" [style.border-color]="getTrackColor(session.track)">
          <mat-card-header>
            <mat-card-title>{{ session.title }}</mat-card-title>
            <mat-card-subtitle>
              {{ session.start_time | date:'shortTime' }} - {{ session.end_time | date:'shortTime' }}
            </mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <p *ngIf="session.description">{{ session.description }}</p>
            <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
              <span *ngIf="session.track" style="background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:4px;font-size:12px">
                {{ session.track }}
              </span>
              <span *ngIf="session.room" style="background:#f3e5f5;color:#7b1fa2;padding:2px 8px;border-radius:4px;font-size:12px">
                {{ session.room }}
              </span>
            </div>
            <div *ngIf="session.speakers && session.speakers.length > 0" style="margin-top:12px">
              <div *ngFor="let speaker of session.speakers" style="display:flex;align-items:center;gap:8px;margin-top:4px">
                <mat-icon style="font-size:20px;width:20px;height:20px">person</mat-icon>
                <span>{{ speaker.name }}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <p *ngIf="filteredSessions.length === 0" style="text-align:center;color:#666;margin-top:48px">
        No sessions found for this track.
      </p>
    </div>
  `,
})
export class AgendaComponent implements OnInit {
  event: Event | null = null;
  sessions: Session[] = [];
  filteredSessions: Session[] = [];
  tracks: string[] = [];
  selectedTrack: string | null = null;

  private trackColors: Record<string, string> = {};
  private colors = ['#3f51b5', '#f44336', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4'];

  constructor(private route: ActivatedRoute, private eventService: EventService) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.eventService.getEvent(id).subscribe(event => this.event = event);
    this.eventService.getSessions(id).subscribe(sessions => {
      this.sessions = sessions;
      this.filteredSessions = sessions;
      this.tracks = [...new Set(sessions.map(s => s.track).filter(Boolean) as string[])];
      this.tracks.forEach((track, i) => {
        this.trackColors[track] = this.colors[i % this.colors.length];
      });
    });
  }

  filterByTrack(track: string | null) {
    this.selectedTrack = track;
    this.filteredSessions = track
      ? this.sessions.filter(s => s.track === track)
      : this.sessions;
  }

  getTrackColor(track?: string): string {
    return track ? (this.trackColors[track] || '#999') : '#999';
  }
}
