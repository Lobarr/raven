import { observable, action, computed } from "mobx";
import { DEFAULT_THEME } from "utils/constants";
import { Theme } from "types/antdProps";

export default class AppStore {
  @observable theme: Theme = DEFAULT_THEME;

  @action setTheme(theme: Theme): void {
    this.theme = theme;
  }

  @computed get isDarkThemed(): boolean {
    return this.theme === "dark";
  }
}
