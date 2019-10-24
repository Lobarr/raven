import { RouteProps } from 'react-router-dom';

// pages
import { App } from 'pages/';
import { RouteNotFound } from 'components/';

const routes: RouteProps[] = [
  {
    path: '/',
    exact: true,
    component: App,
  },
  {
    path: '*',
    component: RouteNotFound,
  },
];

export default routes;
