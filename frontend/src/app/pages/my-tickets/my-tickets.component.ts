import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';

import { TicketService } from '../../services/ticket.service';
import { Ticket } from '../../models/interfaces';

@Component({
  selector: 'app-my-tickets',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatListModule],
  template: `
    <div class="page-header">
      <h1>My Tickets</h1>
    </div>

    <div class="card-grid">
      <mat-card *ngFor="let ticket of tickets">
        <mat-card-header>
          <mat-card-title>{{ ticket.event_title }}</mat-card-title>
          <mat-card-subtitle>{{ ticket.ticket_type_name }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>
            <span class="status-chip" [ngClass]="{
              'published': ticket.payment_status === 'completed',
              'draft': ticket.payment_status === 'pending',
              'cancelled': ticket.payment_status === 'failed' || ticket.payment_status === 'refunded'
            }">
              {{ ticket.payment_status }}
            </span>
          </p>
          <p style="margin-top:8px">Purchased: {{ ticket.purchased_at | date:'medium' }}</p>
          <div *ngIf="ticket.qr_code" style="margin-top:16px;text-align:center;padding:16px;background:#f5f5f5;border-radius:8px">
            <mat-icon style="font-size:64px;width:64px;height:64px;color:#3f51b5">qr_code_2</mat-icon>
            <p style="font-family:monospace;margin-top:8px">{{ ticket.qr_code }}</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <p *ngIf="tickets.length === 0" style="text-align:center;color:#666;margin-top:48px">
      You don't have any tickets yet. Browse events and purchase tickets to see them here.
    </p>
  `,
})
export class MyTicketsComponent implements OnInit {
  tickets: Ticket[] = [];

  constructor(private ticketService: TicketService) {}

  ngOnInit() {
    this.ticketService.getMyTickets().subscribe(tickets => this.tickets = tickets);
  }
}
