import axios, {Method as HTTPMethod, AxiosResponse} from "axios";

export type ApiRequestContext = {
  endpoint: string;
  method?: HTTPMethod;
  data?: object;
  params?: object;
}

export const DEV_API_ENDPOINT = "http://localhost:3001/raven"
export const API_TOKEN_KEY = "raven";

export default class Api {
  static setToken(token: string): void {
    sessionStorage.setItem(API_TOKEN_KEY, token);
  }

  static getToken(): string | null {
    return sessionStorage.getItem(API_TOKEN_KEY);
  }

  static isAuthenticated(): boolean {
    return Api.getToken() !== null;
  }

  static async makeRequest(payload: ApiRequestContext) {
    return axios({
      baseURL: process.env.NODE_ENV === "production" ? process.env.REACT_APP_API : DEV_API_ENDPOINT,
      url: payload.endpoint,
      method: payload.method ? payload.method : "get",
      headers: {
        "x-raven-token": Api.getToken()
      },
      data: payload.data,
      params: payload.params
    });
  }
}
