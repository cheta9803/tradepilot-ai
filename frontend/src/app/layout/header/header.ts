import { Component, inject } from '@angular/core';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { LayoutService } from '../services/layout.service';

@Component({
  selector: 'app-header',
  imports: [
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  readonly layout = inject(LayoutService);

  toggleSidebar(): void {
    this.layout.toggleSidebar();
  }
}