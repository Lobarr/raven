import React, { ReactElement } from "react";

import AppRouter, { Props } from "components/AppRouter";
import { shallow, ShallowWrapper } from "enzyme";
import { RouteProps, Route, Switch } from "react-router";
import PrivateRoute from "components/PrivateRoute";

describe("Approuter", () => {
  const makeComponent = (props: Props): ShallowWrapper => {
    return shallow(<AppRouter {...props} />);
  };
  it("should render given routes", () => {
    const someRoute = (): ReactElement => <div>some route</div>;
    const someOtherRoute = (): ReactElement => <div>some other route</div>;

    const expectedPublicRoutes: RouteProps[] = [
      {
        path: "/some-path",
        component: someRoute
      }
    ];
    const expectedPrivateRoutes: RouteProps[] = [
      {
        path: "/some-other-path",
        component: someOtherRoute
      }
    ];
    const wrapper = makeComponent({
      publicRoutes: expectedPublicRoutes,
      privateRoutes: expectedPrivateRoutes
    });
    
    const renderedPublicRoutes = wrapper.find(Route);
    const renderedPrivateRoutes = wrapper.find(PrivateRoute);


    expect(renderedPublicRoutes.length).toEqual(expectedPublicRoutes.length);
    expectedPublicRoutes.forEach((expectedRoute, index) => {
      expect(renderedPublicRoutes.at(index).props()).toEqual(expectedRoute);
    });
    expectedPrivateRoutes.forEach((expectedRoute, index) => {
      expect(renderedPrivateRoutes.at(index).props()).toEqual(expectedRoute);
    });
  });

  it("should use switch router", () => {
    const wrapper = makeComponent({ publicRoutes: [], privateRoutes: [] });
    expect(wrapper.find(Switch)).toHaveLength(1);
  });
});
