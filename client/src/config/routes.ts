import { RouteProps } from 'react-router-dom';

// pages
import { App } from 'pages/';
import { NoMatch } from 'components/';

const routes: RouteProps[] = [
  {
    path: '/',
    exact: true,
    component: App
  },
  {
    path: '*',
    component: NoMatch
  }
];

export default routes;
