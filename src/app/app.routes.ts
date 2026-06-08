import { Routes } from '@angular/router';
import { DashboardLayoutComponentComponent } from './dashboard-layout-component/dashboard-layout-component.component';
import { CvUploadComponentComponent } from './cv-upload-component/cv-upload-component.component';
import { CandidatesComponentComponent } from './candidates-component/candidates-component.component';
import { OverviewComponentComponent } from './overview-component/overview-component.component';
import { LoginComponentComponent } from './login-component/login-component.component';
import { SettingsComponentComponent } from './settings-component/settings-component.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponentComponent
  },
  {
    path: '',
    component: DashboardLayoutComponentComponent,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        component: OverviewComponentComponent,
        pathMatch: 'full'
      },
      {
        path: 'upload',
        component: CvUploadComponentComponent
      },
      {
        path: 'candidates',
        component: CandidatesComponentComponent
      },
      {
        path: 'settings',
        component: SettingsComponentComponent
      }
    ]
  }
];
