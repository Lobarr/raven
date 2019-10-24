import React, { ReactElement } from 'react';

import { AppRouter } from 'components/';
import routes from 'config/routes';

export default function App(): ReactElement {
  return (
    <div className="app">
      <AppRouter routes={routes} />
    </div>
  );
}
