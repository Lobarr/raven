import { Method as HTTPMethod} from "axios";

export type Insight = {
  _id: string;
  method: HTTPMethod;
  service_id: string;
  path: string;
  remote_ip: string;
  scheme: string;
  status_code: number;
  content_type: string;
  elapsed_time: number;
  cache: boolean;
}
