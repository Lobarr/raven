import React, { ReactElement } from "react";

import AppRouter, { Props } from "components/AppRouter";
import { shallow, ShallowWrapper } from "enzyme";
import { RouteProps, Route, Switch } from "react-router";

describe("Approuter", () => {
  const makeComponent = (props: Props): ShallowWrapper => {
    return shallow(<AppRouter {...props} />);
  };
  it("should render given routes", () => {
    const someRoute = (): ReactElement => <div>some route</div>;
    const someOtherRoute = (): ReactElement => <div>some other route</div>;

    const expectedRoutes: RouteProps[] = [
      {
        path: "/some-path",
        component: someRoute
      },
      {
        path: "/some-other-path",
        component: someOtherRoute
      }
    ];
    const wrapper = makeComponent({
      routes: expectedRoutes
    });
    const renderedRoutes = wrapper.find(Route);

    expect(renderedRoutes.length).toEqual(expectedRoutes.length);
    expectedRoutes.forEach((expectedRoute, index) => {
      expect(renderedRoutes.at(index).props()).toEqual(expectedRoute);
    });
  });

  it("should use switch router", () => {
    const wrapper = makeComponent({ routes: [] });
    expect(wrapper.find(Switch)).toHaveLength(1);
  });
});
