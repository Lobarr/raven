import { RouteProps } from "react-router-dom";
import { RouteNotFound } from "pages/";
import Login from "pages/Login";

export const publicRoutes: RouteProps[] = [
  {
    path: "/login",
    component: Login
  },
  {
    path: "*",
    component: RouteNotFound
  }
];
export const privateRoutes: RouteProps[] = [
  {
    path: "donno",
    component: RouteNotFound
  }
];
