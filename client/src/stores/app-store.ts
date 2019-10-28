import { observable, action } from 'mobx';

export default class AppStore {
  @observable theme = 'dark';

  @action setTheme(theme: string): void {
    this.theme = theme;
  }
}

export const makeAppStore = (): AppStore => {
  return new AppStore();
};
