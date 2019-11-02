import { RouteProps } from "react-router-dom";
import { RouteNotFound } from "pages/";

const routes: RouteProps[] = [
  {
    path: "*",
    component: RouteNotFound
  }
];

export default routes;
