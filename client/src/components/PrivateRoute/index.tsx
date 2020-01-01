import React from "react";
import { Route, Redirect, RouteProps } from "react-router-dom";
import { useObserver } from "mobx-react";
import { useAppContext } from "stores/appContext";


export default function PrivateRoute({ component: Component, ...rest }: RouteProps){
  const appContext = useAppContext();
  const { stores } = appContext;
  const { appStore } = stores;


  return useObserver(() => (
    <Route
      {...rest}
      render={(props) => {
        return appStore.isLoggedIn ? (
          <Component {...props} />
        ) : (
          <Redirect to={{ pathname: "/login" }} />
        )
      }}
    />
  ));
}
