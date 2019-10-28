import { observable, action, computed } from 'mobx';
import { DEFAULT_THEME } from 'utils/constants';

export default class AppStore {
  @observable theme = DEFAULT_THEME;

  @action setTheme(theme: string): void {
    this.theme = theme;
  }

  @computed get isDarkThemed(): boolean {
    return this.theme === "dark";
  }
}
