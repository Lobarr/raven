import React, { ReactElement } from "react";
import { Switch, Route, RouteProps } from "react-router-dom";
import "./index.scss";

export type Props = {
  routes: RouteProps[];
  children?: ReactElement;
};

export default function AppRouter(props: Props): ReactElement {
  return (
    <div className="appRouter">
      <Switch>
        {props.routes.map((route, index) => (
          <Route key={index.toString()} {...route} />
        ))}
      </Switch>
    </div>
  );
}
