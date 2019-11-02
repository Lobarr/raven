import { RouterStore, SynchronizedHistory } from "mobx-react-router";
import AppStore from "stores/appStore";

type Stores = {
  routerStore: RouterStore;
  appStore: AppStore;
  history: SynchronizedHistory;
};

export default Stores;
