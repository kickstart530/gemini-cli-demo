import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/events', pathMatch: 'full' },
  {
    path: 'events',
    loadComponent: () => import('./pages/event-list/event-list.component').then(m => m.EventListComponent),
  },
  {
    path: 'events/create',
    loadComponent: () => import('./pages/event-form/event-form.component').then(m => m.EventFormComponent),
  },
  {
    path: 'events/:id',
    loadComponent: () => import('./pages/event-detail/event-detail.component').then(m => m.EventDetailComponent),
  },
  {
    path: 'events/:id/edit',
    loadComponent: () => import('./pages/event-form/event-form.component').then(m => m.EventFormComponent),
  },
  {
    path: 'events/:id/analytics',
    loadComponent: () => import('./pages/analytics/analytics.component').then(m => m.AnalyticsComponent),
  },
  {
    path: 'events/:id/agenda',
    loadComponent: () => import('./pages/agenda/agenda.component').then(m => m.AgendaComponent),
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent),
  },
  {
    path: 'my-tickets',
    loadComponent: () => import('./pages/my-tickets/my-tickets.component').then(m => m.MyTicketsComponent),
  },
  {
    path: 'payment/success',
    loadComponent: () => import('./pages/payment-success/payment-success.component').then(m => m.PaymentSuccessComponent),
  },
];
