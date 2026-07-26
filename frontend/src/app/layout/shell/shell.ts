import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { MatSidenavModule } from '@angular/material/sidenav';

import { Header } from '../header/header';
import { Sidebar } from '../sidebar/sidebar';
import { LayoutService } from '../services/layout.service';

@Component({
  selector: 'app-shell',
  imports: [
    RouterOutlet,
    MatSidenavModule,
    Header,
    Sidebar,
  ],
  templateUrl: './shell.html',
  styleUrl: './shell.scss',
})
export class Shell {
  readonly layout = inject(LayoutService);
}