import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';

import { EventService } from '../../services/event.service';
import { Event } from '../../models/interfaces';

@Component({
  selector: 'app-event-list',
  standalone: true,
  imports: [
    CommonModule, RouterModule, FormsModule,
    MatCardModule, MatButtonModule, MatInputModule, MatFormFieldModule, MatChipsModule, MatIconModule,
  ],
  template: `
    <div class="page-header">
      <h1>Discover Events</h1>
      <mat-form-field appearance="outline" style="width: 100%; margin-top: 16px">
        <mat-label>Search events...</mat-label>
        <input matInput [(ngModel)]="searchQuery" (ngModelChange)="onSearch()" placeholder="Search by title">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>
    </div>

    <div class="card-grid">
      <mat-card *ngFor="let event of events" class="event-card" [routerLink]="['/events', event.id]">
        <img *ngIf="event.image_url" mat-card-image [src]="event.image_url" [alt]="event.title">
        <div *ngIf="!event.image_url" style="height:140px;background:#e0e0e0;display:flex;align-items:center;justify-content:center">
          <mat-icon style="font-size:48px;width:48px;height:48px;color:#999">event</mat-icon>
        </div>
        <mat-card-header>
          <mat-card-title>{{ event.title }}</mat-card-title>
          <mat-card-subtitle>
            <mat-icon style="font-size:16px;vertical-align:middle">place</mat-icon>
            {{ event.venue || 'TBD' }}
          </mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p style="margin-top:8px">
            <mat-icon style="font-size:16px;vertical-align:middle">calendar_today</mat-icon>
            {{ event.date | date:'mediumDate' }}
          </p>
          <p>
            <span class="status-chip" [ngClass]="event.status">{{ event.status }}</span>
            <span style="margin-left:12px;color:#666">{{ event.attendee_count || 0 }} / {{ event.capacity }} registered</span>
          </p>
        </mat-card-content>
      </mat-card>
    </div>

    <p *ngIf="events.length === 0" style="text-align:center;color:#666;margin-top:48px">
      No events found. Try a different search or check back later.
    </p>
  `,
})
export class EventListComponent implements OnInit {
  events: Event[] = [];
  searchQuery = '';

  constructor(private eventService: EventService) {}

  ngOnInit() {
    this.loadEvents();
  }

  loadEvents() {
    this.eventService.getEvents({ search: this.searchQuery || undefined }).subscribe({
      next: events => this.events = events,
    });
  }

  onSearch() {
    this.loadEvents();
  }
}
