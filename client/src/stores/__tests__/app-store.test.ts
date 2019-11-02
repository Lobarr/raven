import AppStore from "stores/app-store";
import { Theme } from "types/antdProps";

describe("AppStore", () => {
  it("should set theme value", () => {
    const appStore = new AppStore();
    const expectedTheme = "some-theme" as Theme;
    appStore.setTheme(expectedTheme);
    expect(appStore.theme).toEqual(expectedTheme);
  });

  it("should check if currently set theme is dark", () => {
    const appStore = new AppStore();
    expect(appStore.isDarkThemed).toBeTruthy();
  });
});
