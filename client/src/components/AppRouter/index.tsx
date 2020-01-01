import React, { ReactElement } from "react";
import { Switch, Route, RouteProps } from "react-router-dom";
import { PrivateRoute } from "components";
import { useObserver } from "mobx-react";
import { v4 } from "uuid";
import "./index.scss";


export type Props = {
  publicRoutes: RouteProps[];
  privateRoutes: RouteProps[];
  children?: ReactElement;
};

export default function AppRouter(props: Props): ReactElement {
  const { privateRoutes, publicRoutes } = props;

  return useObserver(() => (
    <div className="appRouter">
      <Switch>
        {privateRoutes.map((route, index) => (
          <PrivateRoute key={ index.toString() } { ...route } />
        ))}
        {publicRoutes.map((route, index) => (
          <Route key={ index.toString() } { ...route } />
        ))}
      </Switch>
    </div>
  ));
}
