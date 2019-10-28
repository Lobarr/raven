import { createBrowserHistory } from 'history';
import { RouterStore, syncHistoryWithStore } from 'mobx-react-router';

const broserHistory = createBrowserHistory();
const routerStore = new RouterStore();
const history = syncHistoryWithStore(broserHistory, routerStore);

export const makeRouterStore = (): RouterStore => {
  return routerStore;
};

export { history };
