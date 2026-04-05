import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';

import { EventService } from '../../services/event.service';
import { TicketService } from '../../services/ticket.service';
import { AuthService } from '../../services/auth.service';
import { Event, Session, Attendee } from '../../models/interfaces';

@Component({
  selector: 'app-event-detail',
  standalone: true,
  imports: [
    CommonModule, RouterModule,
    MatCardModule, MatButtonModule, MatIconModule, MatTabsModule,
    MatListModule, MatDialogModule, MatSnackBarModule, MatSelectModule,
  ],
  template: `
    <div *ngIf="event">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <div>
          <h1>{{ event.title }}</h1>
          <span class="status-chip" [ngClass]="event.status">{{ event.status }}</span>
        </div>
        <div *ngIf="isOrganizer()">
          <button mat-button [routerLink]="['/events', event.id, 'edit']">
            <mat-icon>edit</mat-icon> Edit
          </button>
          <button mat-button (click)="publishEvent()" *ngIf="event.status === 'draft'">
            <mat-icon>publish</mat-icon> Publish
          </button>
          <button mat-button [routerLink]="['/events', event.id, 'analytics']">
            <mat-icon>analytics</mat-icon> Analytics
          </button>
          <button mat-button color="warn" (click)="deleteEvent()">
            <mat-icon>delete</mat-icon> Delete
          </button>
        </div>
      </div>

      <img *ngIf="event.image_url" [src]="event.image_url" style="width:100%;max-height:400px;object-fit:cover;border-radius:8px;margin-bottom:24px" [alt]="event.title">

      <mat-tab-group>
        <mat-tab label="Details">
          <div style="padding:24px 0">
            <mat-card>
              <mat-card-content>
                <p><strong>Date:</strong> {{ event.date | date:'fullDate' }}</p>
                <p><strong>Venue:</strong> {{ event.venue || 'TBD' }}</p>
                <p><strong>Capacity:</strong> {{ event.capacity }}</p>
                <p style="margin-top:16px">{{ event.description }}</p>
              </mat-card-content>
            </mat-card>

            <mat-card style="margin-top:16px" *ngIf="event.ticket_types && event.ticket_types.length > 0">
              <mat-card-header><mat-card-title>Tickets</mat-card-title></mat-card-header>
              <mat-card-content>
                <mat-list>
                  <mat-list-item *ngFor="let tt of event.ticket_types">
                    <span matListItemTitle>{{ tt.name }}</span>
                    <span matListItemLine>{{ tt.price === 0 ? 'Free' : ('$' + tt.price.toFixed(2)) }} - {{ tt.quantity }} available</span>
                    <button mat-raised-button color="primary" matListItemMeta (click)="purchaseTicket(tt.id)" *ngIf="auth.isLoggedIn()">
                      {{ tt.price === 0 ? 'Register' : 'Buy Ticket' }}
                    </button>
                  </mat-list-item>
                </mat-list>
              </mat-card-content>
            </mat-card>

            <div style="margin-top:16px" *ngIf="auth.isLoggedIn()">
              <button mat-raised-button color="accent" (click)="registerForEvent()">
                <mat-icon>how_to_reg</mat-icon> Register for Event
              </button>
            </div>
          </div>
        </mat-tab>

        <mat-tab label="Agenda">
          <div style="padding:24px 0">
            <button mat-button [routerLink]="['/events', event.id, 'agenda']">
              <mat-icon>open_in_new</mat-icon> Full Agenda View
            </button>
            <mat-list>
              <mat-list-item *ngFor="let session of sessions">
                <span matListItemTitle>{{ session.title }}</span>
                <span matListItemLine>
                  {{ session.start_time | date:'shortTime' }} - {{ session.end_time | date:'shortTime' }}
                  <span *ngIf="session.track"> | {{ session.track }}</span>
                  <span *ngIf="session.room"> | {{ session.room }}</span>
                </span>
              </mat-list-item>
            </mat-list>
            <p *ngIf="sessions.length === 0" style="color:#666">No sessions scheduled yet.</p>
          </div>
        </mat-tab>

        <mat-tab label="Attendees" *ngIf="isOrganizer()">
          <div style="padding:24px 0">
            <p style="margin-bottom:16px">{{ attendees.length }} registered attendees</p>
            <mat-list>
              <mat-list-item *ngFor="let a of attendees">
                <mat-icon matListItemIcon>{{ a.check_in_status ? 'check_circle' : 'radio_button_unchecked' }}</mat-icon>
                <span matListItemTitle>{{ a.user_name }}</span>
                <span matListItemLine>{{ a.user_email }} - Registered {{ a.registration_date | date:'medium' }}</span>
              </mat-list-item>
            </mat-list>
          </div>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
})
export class EventDetailComponent implements OnInit {
  event: Event | null = null;
  sessions: Session[] = [];
  attendees: Attendee[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eventService: EventService,
    private ticketService: TicketService,
    public auth: AuthService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.eventService.getEvent(id).subscribe(event => this.event = event);
    this.eventService.getSessions(id).subscribe(sessions => this.sessions = sessions);
    if (this.auth.isLoggedIn()) {
      this.eventService.getAttendees(id).subscribe({
        next: attendees => this.attendees = attendees,
        error: () => {},
      });
    }
  }

  isOrganizer(): boolean {
    return this.event?.organizer_id === this.auth.currentUser()?.id;
  }

  publishEvent() {
    if (!this.event) return;
    this.eventService.publishEvent(this.event.id).subscribe(event => {
      this.event = event;
      this.snackBar.open('Event published!', 'Close', { duration: 3000 });
    });
  }

  deleteEvent() {
    if (!this.event || !confirm('Are you sure you want to delete this event?')) return;
    this.eventService.deleteEvent(this.event.id).subscribe(() => {
      this.snackBar.open('Event deleted', 'Close', { duration: 3000 });
      this.router.navigate(['/events']);
    });
  }

  registerForEvent() {
    if (!this.event) return;
    this.eventService.registerForEvent(this.event.id).subscribe({
      next: () => this.snackBar.open('Registered successfully!', 'Close', { duration: 3000 }),
      error: err => this.snackBar.open(err.error?.detail || 'Registration failed', 'Close', { duration: 3000 }),
    });
  }

  purchaseTicket(ticketTypeId: number) {
    if (!this.event) return;
    this.ticketService.purchaseTicket(this.event.id, ticketTypeId).subscribe({
      next: ticket => {
        this.snackBar.open('Ticket purchased!', 'View Tickets', { duration: 5000 })
          .onAction().subscribe(() => this.router.navigate(['/my-tickets']));
      },
      error: err => this.snackBar.open(err.error?.detail || 'Purchase failed', 'Close', { duration: 3000 }),
    });
  }
}
