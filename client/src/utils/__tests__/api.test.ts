import axios, { Method } from "axios";
import Api, { API_TOKEN_KEY } from "utils/api";

jest.mock("axios");

describe("Api", () => {
  it("should get token from the session storage", () => {
    Api.getToken();
    expect(sessionStorage.getItem).toHaveBeenCalledWith(API_TOKEN_KEY)
  })

  it("should set token in the session storage", () => {
    const mockToken = "some-token";
    Api.setToken(mockToken);
    expect(sessionStorage.setItem).toHaveBeenCalledWith(API_TOKEN_KEY, mockToken);
  })

  it("should make api request", async () => {
    const requestContext = {
      endpoint: "some-endpoint",
      method: "GET" as Method,
      data: {},
      params: {}
    };

    await Api.makeRequest(requestContext);

    expect(axios.mock.calls[0][0]).toHaveProperty("baseURL");
    expect(axios.mock.calls[0][0]).toHaveProperty("url", requestContext.endpoint);
    expect(axios.mock.calls[0][0]).toHaveProperty("method", requestContext.method);
    expect(axios.mock.calls[0][0]).toHaveProperty("headers");
    expect(axios.mock.calls[0][0]).toHaveProperty("data", requestContext.data);
    expect(axios.mock.calls[0][0]).toHaveProperty("params", requestContext.params);
  })
});
