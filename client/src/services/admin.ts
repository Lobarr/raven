import Api from "utils/api";
import { Admin } from "types/admin";
import { AxiosResponse } from "axios";

const BASE_ENDPOINT = "/admin";

export default class AdminUtil {
  static async login(username: string, password: string) {
    return Api.makeRequest({
      endpoint: `${BASE_ENDPOINT}/login`,
      method: "POST",
      data: { username, password }
    })
  }

  static async update(payload: object) {
    return Api.makeRequest({
      endpoint: BASE_ENDPOINT,
      method: "PATCH",
      data: payload
    })
  }

  static async create(payload: object) {
    return Api.makeRequest({
      endpoint: BASE_ENDPOINT,
      method: "POST",
      data: payload
    })
  }

  static async get(payload: object) {
    return Api.makeRequest({
      endpoint: BASE_ENDPOINT,
      method: "GET",
      params: payload
    })
  }

  static async delete(id: string) {
    return Api.makeRequest({
      endpoint: BASE_ENDPOINT,
      method: "DELETE",
      params: { id }
    })
  }
}
