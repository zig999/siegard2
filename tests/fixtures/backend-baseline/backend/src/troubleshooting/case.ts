export type CaseStatus = 'open' | 'investigating' | 'resolved';
export class Case {
  constructor(private readonly id: string) {}
}
