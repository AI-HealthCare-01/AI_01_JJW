import { createBrowserRouter } from 'react-router';
import { LoginPage } from './components/LoginPage';
import { ServiceSelectPage } from './components/ServiceSelectPage';
import { SurveyPage } from './components/SurveyPage';
import { DashboardPage } from './components/DashboardPage';

export const router = createBrowserRouter([
  { path: '/', Component: LoginPage },
  { path: '/select-service', Component: ServiceSelectPage },
  { path: '/survey', Component: SurveyPage },
  { path: '/dashboard', Component: DashboardPage },
]);
