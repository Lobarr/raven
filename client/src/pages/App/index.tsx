import React, { ReactElement } from 'react';
import './index.scss';

import { AppRouter } from 'components/';
import AppContext, { initAppState } from 'stores/app-context';
import routes from 'config/routes';

export default function App(): ReactElement {
  return (
    <div className="app">
      <AppContext.Provider value={initAppState}>
        <AppRouter routes={routes} />
      </AppContext.Provider>
    </div>
  );
}
