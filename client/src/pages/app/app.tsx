import React from 'react';

import { Router } from 'components/';
import routes from 'config/routes';

export default function App() {
  return (
    <div className="app">
      <Router routes={routes} />
    </div>
  );
}
