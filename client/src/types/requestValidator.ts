import { Method as HTTPMethod } from "axios";

export type PasswordPolicy = {
  length: number;
  upper_case_count: number;
  numbers_count: number;
  specials_count: number;
  non_letters_count: number;
  strength: number;
}

export type RequestValidator = {
  _id: string;
  service_id: string;
  method: HTTPMethod;
  schema: object;
  password_filed: string;
  password_policy: PasswordPolicy;
  err_response_code: number;
}
