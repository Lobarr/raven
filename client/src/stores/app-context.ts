import { createContext } from 'react';
import AppState from 'types/app-state';

import { AppStore, makeRouterStore } from 'stores/';

export const initAppState: AppState = {
  stores: {
    routerStore: makeRouterStore(),
    appStore: new AppStore()
  }
};

const AppContext = createContext(initAppState);

export default AppContext;
