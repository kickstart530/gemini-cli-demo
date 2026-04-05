import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { EventService } from '../../services/event.service';

interface TicketTypeForm {
  name: string;
  price: number;
  quantity: number;
}

@Component({
  selector: 'app-event-form',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatButtonModule, MatInputModule, MatFormFieldModule, MatIconModule, MatSnackBarModule,
  ],
  template: `
    <div class="page-header">
      <h1>{{ isEdit ? 'Edit Event' : 'Create Event' }}</h1>
    </div>

    <mat-card>
      <mat-card-content>
        <form (ngSubmit)="onSubmit()" style="display:flex;flex-direction:column;gap:16px">
          <mat-form-field appearance="outline">
            <mat-label>Title</mat-label>
            <input matInput [(ngModel)]="form.title" name="title" required>
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Description</mat-label>
            <textarea matInput [(ngModel)]="form.description" name="description" rows="4"></textarea>
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Venue</mat-label>
            <input matInput [(ngModel)]="form.venue" name="venue">
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Date & Time</mat-label>
            <input matInput type="datetime-local" [(ngModel)]="form.date" name="date" required>
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Capacity</mat-label>
            <input matInput type="number" [(ngModel)]="form.capacity" name="capacity" required>
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>Image URL</mat-label>
            <input matInput [(ngModel)]="form.image_url" name="image_url">
          </mat-form-field>

          <div *ngIf="!isEdit">
            <h3>Ticket Types</h3>
            <div *ngFor="let tt of ticketTypes; let i = index" style="display:flex;gap:8px;margin-bottom:8px">
              <mat-form-field appearance="outline" style="flex:2">
                <mat-label>Name</mat-label>
                <input matInput [(ngModel)]="tt.name" [name]="'tt_name_' + i">
              </mat-form-field>
              <mat-form-field appearance="outline" style="flex:1">
                <mat-label>Price</mat-label>
                <input matInput type="number" [(ngModel)]="tt.price" [name]="'tt_price_' + i">
              </mat-form-field>
              <mat-form-field appearance="outline" style="flex:1">
                <mat-label>Qty</mat-label>
                <input matInput type="number" [(ngModel)]="tt.quantity" [name]="'tt_qty_' + i">
              </mat-form-field>
              <button mat-icon-button type="button" (click)="removeTicketType(i)" color="warn">
                <mat-icon>delete</mat-icon>
              </button>
            </div>
            <button mat-button type="button" (click)="addTicketType()">
              <mat-icon>add</mat-icon> Add Ticket Type
            </button>
          </div>

          <div style="display:flex;gap:16px;margin-top:16px">
            <button mat-raised-button color="primary" type="submit">
              {{ isEdit ? 'Update' : 'Create' }} Event
            </button>
            <button mat-button type="button" (click)="cancel()">Cancel</button>
          </div>
        </form>
      </mat-card-content>
    </mat-card>
  `,
})
export class EventFormComponent implements OnInit {
  isEdit = false;
  eventId: number | null = null;
  form = {
    title: '',
    description: '',
    venue: '',
    date: '',
    capacity: 100,
    image_url: '',
  };
  ticketTypes: TicketTypeForm[] = [
    { name: 'General Admission', price: 0, quantity: 100 },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eventService: EventService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEdit = true;
      this.eventId = Number(id);
      this.eventService.getEvent(this.eventId).subscribe(event => {
        this.form.title = event.title;
        this.form.description = event.description || '';
        this.form.venue = event.venue || '';
        this.form.date = event.date.slice(0, 16);
        this.form.capacity = event.capacity;
        this.form.image_url = event.image_url || '';
      });
    }
  }

  addTicketType() {
    this.ticketTypes.push({ name: '', price: 0, quantity: 50 });
  }

  removeTicketType(index: number) {
    this.ticketTypes.splice(index, 1);
  }

  onSubmit() {
    const data: any = {
      ...this.form,
      date: new Date(this.form.date).toISOString(),
    };

    if (this.isEdit && this.eventId) {
      this.eventService.updateEvent(this.eventId, data).subscribe({
        next: () => {
          this.snackBar.open('Event updated!', 'Close', { duration: 3000 });
          this.router.navigate(['/events', this.eventId]);
        },
        error: err => this.snackBar.open(err.error?.detail || 'Update failed', 'Close', { duration: 3000 }),
      });
    } else {
      data.ticket_types = this.ticketTypes.filter(tt => tt.name);
      this.eventService.createEvent(data).subscribe({
        next: event => {
          this.snackBar.open('Event created!', 'Close', { duration: 3000 });
          this.router.navigate(['/events', event.id]);
        },
        error: err => this.snackBar.open(err.error?.detail || 'Creation failed', 'Close', { duration: 3000 }),
      });
    }
  }

  cancel() {
    if (this.isEdit && this.eventId) {
      this.router.navigate(['/events', this.eventId]);
    } else {
      this.router.navigate(['/events']);
    }
  }
}
