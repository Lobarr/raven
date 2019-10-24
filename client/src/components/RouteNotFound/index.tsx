import React, { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';

export default function RouteNotFound(): ReactElement {
  const location = useLocation();

  return (
    <div>
      <h3>
        No match for <code>{location.pathname}</code>
      </h3>
    </div>
  );
}
