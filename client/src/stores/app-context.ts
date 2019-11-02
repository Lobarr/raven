import { createContext } from "react";
import { createBrowserHistory } from "history";
import { RouterStore, syncHistoryWithStore } from "mobx-react-router";
import AppState from "types/appState";

import AppStore from "stores/app-store";

const broserHistory = createBrowserHistory();
const routerStore = new RouterStore();
const history = syncHistoryWithStore(broserHistory, routerStore);

export const initAppState: AppState = {
  stores: {
    routerStore: routerStore,
    appStore: new AppStore(),
    history: history
  }
};

const AppContext = createContext(initAppState);

export default AppContext;
