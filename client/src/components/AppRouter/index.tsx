import React, { ReactElement } from 'react';
import { BrowserRouter, Switch, Route, RouteProps } from 'react-router-dom';
import './index.scss';

export type Props = {
  routes: RouteProps[];
};

export default function AppRouter(props: Props): ReactElement {
  return (
    <div className="appRouter">
      <BrowserRouter>
        <Switch>
          {props.routes.map((route, index) => (
            <Route key={index.toString()} {...route} />
          ))}
        </Switch>
      </BrowserRouter>
    </div>
  );
}
