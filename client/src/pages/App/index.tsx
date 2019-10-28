import React, { ReactElement } from 'react';
import { Layout } from 'antd';
import { AppRouter, BasePage } from 'components/';
import AppContext, { initAppState } from 'stores/app-context';
import routes from 'config/routes';
import './index.scss';

export default function App(): ReactElement {
  return (
    <Layout className="app">
      <AppContext.Provider value={initAppState}>
        <BasePage>
          <AppRouter routes={routes} />
        </BasePage>
      </AppContext.Provider>
    </Layout>
  );
}
