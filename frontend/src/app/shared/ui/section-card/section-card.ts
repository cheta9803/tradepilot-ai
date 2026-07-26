import { Component, input } from '@angular/core';

import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-section-card',
  imports: [MatCardModule],
  templateUrl: './section-card.html',
  styleUrl: './section-card.scss',
})
export class SectionCard {
  readonly title = input.required<string>();
}