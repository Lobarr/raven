import React from 'react';

import AppRouter, { Props } from 'components/AppRouter';
import { shallow, render } from 'enzyme';
import { RouteProps, Route } from 'react-router';

describe('Approuter', () => {
  const makeComponent = (props: Props) => shallow(<AppRouter {...props} />);
  it('should render given routes', () => {
    const testComponent = () => <div>some test component</div>;
    const expectedRoutes: RouteProps[] = [
      {
        path: '/some-path',
        component: testComponent
      }
    ];
    const wrapper = makeComponent({
      routes: expectedRoutes
    });

    const renderedRoute = wrapper.find(Route);
    expect(renderedRoute.length).toEqual(expect.length);
    expect(renderedRoute.props()).toEqual(expectedRoutes[0]);
  });
});
