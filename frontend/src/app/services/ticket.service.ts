import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { Ticket, CheckoutSession } from '../models/interfaces';

@Injectable({ providedIn: 'root' })
export class TicketService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  purchaseTicket(eventId: number, ticketTypeId: number): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.api}/events/${eventId}/tickets/purchase`, {
      ticket_type_id: ticketTypeId,
    });
  }

  getTicket(ticketId: number): Observable<Ticket> {
    return this.http.get<Ticket>(`${this.api}/tickets/${ticketId}`);
  }

  getMyTickets(): Observable<Ticket[]> {
    return this.http.get<Ticket[]>(`${this.api}/users/me/tickets`);
  }

  createCheckoutSession(ticketId: number): Observable<CheckoutSession> {
    return this.http.post<CheckoutSession>(`${this.api}/payments/checkout/${ticketId}`, {});
  }
}
