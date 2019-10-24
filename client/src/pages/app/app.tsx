import React, { ReactElement } from 'react';

import { Router } from 'components/';
import routes from 'config/routes';

export default function App(): ReactElement {
  return (
    <div className="app">
      <Router routes={routes} />
    </div>
  );
}
