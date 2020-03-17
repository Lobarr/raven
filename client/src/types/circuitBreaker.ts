export enum CircuitBreakerStatus {
  ON,
  OFF
}

export type CircuitBreaker = {
  _id: string;
  status: CircuitBreakerStatus;
  service_id: string;
  cooldown: number;
  status_code: number[];
  method: string;
  threshold: number;
  period: number;
  tripped_count: number;
}
