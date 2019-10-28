import { RouterStore } from 'mobx-react-router';
import { AppStore } from 'stores/';

type Stores = {
  routerStore: RouterStore;
  appStore: AppStore;
};

export default Stores;
