export type RateLimitRule = {
  _id: string;
  max_requests: number;
  service_id: string;
  timeout: number;
  message: string;
  status_code: number;
} 

export type RateLimitEntry = {
  _id: string;
  rule_id: string;
  host: string;
  count: number;
}
