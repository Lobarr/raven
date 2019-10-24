import { RouteProps } from 'react-router-dom';
import { Progress } from 'antd';
import { RouteNotFound } from 'pages/';

const routes: RouteProps[] = [
  {
    path: '*',
    component: RouteNotFound
  }
];

export default routes;
