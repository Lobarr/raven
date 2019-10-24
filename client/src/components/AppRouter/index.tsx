import React, { ReactElement } from 'react';
import { BrowserRouter, Switch, Route, RouteProps } from 'react-router-dom';

type Props = {
  routes: RouteProps[];
};

export default function AppRouter(props: Props): ReactElement {
  return (
    <BrowserRouter>
      <Switch>
        {props.routes.map((route, index) => (
          <Route key={index.toString()} {...route} />
        ))}
      </Switch>
    </BrowserRouter>
  );
};
