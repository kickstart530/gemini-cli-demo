import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { Event, EventAnalytics, Attendee, Session, Speaker } from '../models/interfaces';

@Injectable({ providedIn: 'root' })
export class EventService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Events
  getEvents(params?: { status?: string; search?: string }): Observable<Event[]> {
    let httpParams = new HttpParams();
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    return this.http.get<Event[]>(`${this.api}/events`, { params: httpParams });
  }

  getEvent(id: number): Observable<Event> {
    return this.http.get<Event>(`${this.api}/events/${id}`);
  }

  createEvent(data: Partial<Event>): Observable<Event> {
    return this.http.post<Event>(`${this.api}/events`, data);
  }

  updateEvent(id: number, data: Partial<Event>): Observable<Event> {
    return this.http.put<Event>(`${this.api}/events/${id}`, data);
  }

  deleteEvent(id: number): Observable<void> {
    return this.http.delete<void>(`${this.api}/events/${id}`);
  }

  publishEvent(id: number): Observable<Event> {
    return this.http.post<Event>(`${this.api}/events/${id}/publish`, {});
  }

  // Registration
  registerForEvent(eventId: number): Observable<Attendee> {
    return this.http.post<Attendee>(`${this.api}/events/${eventId}/register`, {});
  }

  getAttendees(eventId: number): Observable<Attendee[]> {
    return this.http.get<Attendee[]>(`${this.api}/events/${eventId}/attendees`);
  }

  // Sessions
  getSessions(eventId: number): Observable<Session[]> {
    return this.http.get<Session[]>(`${this.api}/events/${eventId}/sessions`);
  }

  createSession(eventId: number, data: Partial<Session>): Observable<Session> {
    return this.http.post<Session>(`${this.api}/events/${eventId}/sessions`, data);
  }

  // Speakers
  getSpeakers(): Observable<Speaker[]> {
    return this.http.get<Speaker[]>(`${this.api}/speakers`);
  }

  createSpeaker(data: Partial<Speaker>): Observable<Speaker> {
    return this.http.post<Speaker>(`${this.api}/speakers`, data);
  }

  // Analytics
  getAnalytics(eventId: number): Observable<EventAnalytics> {
    return this.http.get<EventAnalytics>(`${this.api}/events/${eventId}/analytics`);
  }
}
