import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LayoutService {
  readonly sidenavOpened = signal(true);

  toggleSidebar(): void {
    this.sidenavOpened.update((opened) => !opened);
  }

  openSidebar(): void {
    this.sidenavOpened.set(true);
  }

  closeSidebar(): void {
    this.sidenavOpened.set(false);
  }
}