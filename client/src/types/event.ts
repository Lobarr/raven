export type Event = {
  _id: string;
  circuit_breaker_id: string;
  target: string;
  body: object;
  headers: object;
}
