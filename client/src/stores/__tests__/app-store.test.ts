import AppStore from 'stores/app-store';

describe('AppStore', () => {
  it('should set theme value', () => {
    const appStore = new AppStore();
    const expectedTheme = 'some-theme';
    appStore.setTheme(expectedTheme);
    expect(appStore.theme).toEqual(expectedTheme);
  })

  it('should check if currently set theme is dark', () => {
    const appStore = new AppStore();
    expect(appStore.isDarkThemed).toBeTruthy();
  })
});
