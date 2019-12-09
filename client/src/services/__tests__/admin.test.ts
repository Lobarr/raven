import Admin from "services/admin"
import Api from "utils/api";

describe("Admin", () => {
  const makeRequestMock = jest.spyOn(Api, "makeRequest").mockImplementation(jest.fn());

  beforeEach(() => {
    makeRequestMock.mockClear();
  })

  it("should be able to login as an admin", async () => {
    const mockUsername = "some-username";
    const mockPassword = "some-password";

    await Admin.login(mockUsername, mockPassword);
    
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("endpoint", "/admin/login");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("method", "POST");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("data", {
      username: mockUsername,
      password: mockPassword
    });
  })

  it("should be able to update admin", async () => {
    const mockPayload = {
      username: "some-username"
    }

    await Admin.update(mockPayload);

    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("endpoint", "/admin");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("method", "PATCH");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("data", mockPayload);
  })
  it("should be able to create admin", async () => {
    const mockPayload = {
      username: "some-username",
      email: "some-email"
    }

    await Admin.create(mockPayload);

    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("endpoint", "/admin");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("method", "POST");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("data", mockPayload);
  })
  it("should be able to get admin", async () => {
    const mockPayload = {
      username: "some-username"
    }

    await Admin.get(mockPayload);

    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("endpoint", "/admin");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("method", "GET");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("params", mockPayload);
  })
  it("should be able to delete admin", async () => {
    const mockId = "some-id"

    await Admin.delete(mockId);

    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("endpoint", "/admin");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("method", "DELETE");
    expect(makeRequestMock.mock.calls[0][0]).toHaveProperty("params", { id: mockId});
  })
})
