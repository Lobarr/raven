import React, { ReactElement } from "react";
import { Route, Redirect, RouteProps } from "react-router-dom";
import { useObserver } from "mobx-react";
import { useAppContext } from "stores/appContext";


export default function PrivateRoute({ component: Component, ...otherProps }: RouteProps | any): ReactElement {
  const appContext = useAppContext();
  const { stores } = appContext;
  const { appStore } = stores;

  return useObserver(() => (
    <Route
      {...otherProps}
      render={(props) => (
        appStore.isLoggedIn === true
        ? <Component {...props} />
        : <Redirect to={{ pathname: "/login" }} />
      )}
    />
  ));
}
