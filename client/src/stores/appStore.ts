import { observable, action, computed } from "mobx";
import { DEFAULT_THEME } from "utils/constants";
import { Theme } from "types/antdProps";
import { Admin } from "types/admin";

export default class AppStore {
  @observable theme: Theme = DEFAULT_THEME;
  @observable admin?: Admin;

  @action setTheme(theme: Theme): void {
    this.theme = theme;
  }

  @computed get isDarkThemed(): boolean {
    return this.theme === "dark";
  }
}
