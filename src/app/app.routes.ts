import { Routes } from '@angular/router';
import { DashboardLayoutComponentComponent } from './dashboard-layout-component/dashboard-layout-component.component';
import { CvUploadComponentComponent } from './cv-upload-component/cv-upload-component.component';
import { CandidatesComponentComponent } from './candidates-component/candidates-component.component';
import { OverviewComponentComponent } from './overview-component/overview-component.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardLayoutComponentComponent,
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
      }
    ]
  }
];
