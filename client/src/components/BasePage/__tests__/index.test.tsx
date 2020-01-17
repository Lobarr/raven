import React from "react";
import { shallow, ShallowWrapper } from "enzyme";
import BasePage from "components/BasePage";
import { Layout } from "antd";
import ThemedHeader from "components/ThemedHeader";
import SideMenu from "components/SideMenu";
const { Content } = Layout;

describe("BasePage", () => {
  const makeComponent = (): ShallowWrapper => {
    return shallow(<BasePage />);
  };

  it("should render base page", () => {
    const wrapper = makeComponent();

    expect(wrapper.find(Layout)).toHaveLength(2);
    expect(wrapper.find(ThemedHeader)).toHaveLength(1);
    expect(wrapper.find(SideMenu)).toHaveLength(1);
    expect(wrapper.find(Content)).toHaveLength(1);
  });
});
