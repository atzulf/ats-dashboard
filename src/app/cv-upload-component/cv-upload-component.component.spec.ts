import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CvUploadComponentComponent } from './cv-upload-component.component';

describe('CvUploadComponentComponent', () => {
  let component: CvUploadComponentComponent;
  let fixture: ComponentFixture<CvUploadComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CvUploadComponentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CvUploadComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
