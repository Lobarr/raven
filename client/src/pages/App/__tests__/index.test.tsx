import React from "react";
import { shallow, ShallowWrapper } from "enzyme";

import App from "pages/App";
import { BasePage } from "components";
import AppContext from "stores/appContext";
import { BrowserRouter } from "react-router-dom";

describe("App", () => {
  const makeComponent = (): ShallowWrapper => shallow(<App />);

  it("should render component", () => {
    const wrapper = makeComponent();

    expect(wrapper.find(BrowserRouter)).toHaveLength(1);
    expect(wrapper.find(BasePage)).toHaveLength(1);
    expect(wrapper.find(AppContext.Provider)).toHaveLength(1);
  });
});
