import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-dashboard-layout-component',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './dashboard-layout-component.component.html',
  styleUrl: './dashboard-layout-component.component.css'
})
export class DashboardLayoutComponentComponent {
}
