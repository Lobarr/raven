import React from "react";
import { ShallowWrapper, shallow } from "enzyme";
import ThemedHeader, { Props } from "components/ThemedHeader";
import { Link } from "react-router-dom";
import { Layout } from "antd";

const { Header } = Layout;

describe("ThemedHeader", () => {
  const makeComponent = (props: Props): ShallowWrapper => {
    return shallow(<ThemedHeader {...props} />);
  };

  it("should handle light theme", () => {
    const wrapper = makeComponent({
      theme: "light"
    });
    const renderedSpan = wrapper.find("span");

    expect(renderedSpan.props()).toHaveProperty("style.color", "black");
    expect(renderedSpan.props()).toHaveProperty("style.fontSize");
    expect(renderedSpan.props()).toHaveProperty("style.fontFamily");
    expect(wrapper.find(Header).props()).toHaveProperty(
      "style.backgroundColor",
      "white"
    );
  });

  it("should handle dark theme", () => {
    const wrapper = makeComponent({
      theme: "dark"
    });
    const renderedSpan = wrapper.find("span");

    expect(renderedSpan.props()).toHaveProperty("style.color", "white");
    expect(renderedSpan.props()).toHaveProperty("style.fontSize");
    expect(renderedSpan.props()).toHaveProperty("style.fontFamily");
    expect(wrapper.find(Header).props()).toHaveProperty(
      "style.backgroundColor",
      ""
    );
  });

  it("should link to homepage", () => {
    const wrapper = makeComponent({
      theme: "dark"
    });

    expect(wrapper.find(Link).props()).toHaveProperty("to", "/");
  });
});
