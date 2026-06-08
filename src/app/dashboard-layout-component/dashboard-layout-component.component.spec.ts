import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardLayoutComponentComponent } from './dashboard-layout-component.component';

describe('DashboardLayoutComponentComponent', () => {
  let component: DashboardLayoutComponentComponent;
  let fixture: ComponentFixture<DashboardLayoutComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardLayoutComponentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardLayoutComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
