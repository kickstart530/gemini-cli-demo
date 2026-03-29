export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface TicketType {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

export interface Event {
  id: number;
  title: string;
  description?: string;
  venue?: string;
  date: string;
  capacity: number;
  status: string;
  organizer_id: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
  ticket_types: TicketType[];
  attendee_count?: number;
}

export interface Attendee {
  id: number;
  user_id: number;
  event_id: number;
  registration_date: string;
  check_in_status: boolean;
  checked_in_at?: string;
  user_name: string;
  user_email: string;
}

export interface Ticket {
  id: number;
  attendee_id: number;
  ticket_type_id: number;
  qr_code?: string;
  purchased_at: string;
  ticket_type_name: string;
  event_title: string;
  payment_status: string;
}

export interface Speaker {
  id: number;
  name: string;
  bio?: string;
  photo_url?: string;
  email?: string;
}

export interface Session {
  id: number;
  event_id: number;
  title: string;
  description?: string;
  track?: string;
  room?: string;
  start_time: string;
  end_time: string;
  speakers: Speaker[];
}

export interface EventAnalytics {
  event_id: number;
  event_title: string;
  total_capacity: number;
  total_registrations: number;
  total_checked_in: number;
  check_in_rate: number;
  total_revenue: number;
  tickets_by_type: { type: string; count: number; revenue: number }[];
  registrations_over_time: { date: string; count: number }[];
}

export interface CheckoutSession {
  checkout_url: string;
  session_id: string;
}
