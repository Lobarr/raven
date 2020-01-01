import React, { ReactElement } from "react";
import { Switch, Route, RouteProps } from "react-router-dom";
import "./index.scss";
import PrivateRoute from "components/PrivateRoute";

export type Props = {
  publicRoutes: RouteProps[];
  privateRoutes: RouteProps[];
  children?: ReactElement;
};

export default function AppRouter(props: Props): ReactElement {
  return (
    <div className="appRouter">
      <Switch>
        {props.publicRoutes.map((route, index) => (
          <Route key={index.toString()} {...route} />
        ))}
        {props.privateRoutes.map((route, index) => (
          <PrivateRoute key={index.toString()} {...route} />
        ))}
        
      </Switch>
    </div>
  );
}
