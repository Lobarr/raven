import React, { Suspense } from 'react';
import { BrowserRouter, Switch, Route, RouteProps } from 'react-router-dom';

type Props = {
  routes: RouteProps[];
};

export default function Router(props: Props) {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>testing</div>}>
        <Switch>
          {props.routes.map((route, index) => (
            <Route key={index.toString()} {...route} />
          ))}
        </Switch>
      </Suspense>
    </BrowserRouter>
  );
}
