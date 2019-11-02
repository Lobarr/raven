import React from "react";
import { shallow, ShallowWrapper } from "enzyme";
import SideMenu, { Props } from "components/SideMenu";
import { Theme } from "types/antdProps";
import { Layout, Menu, Icon } from "antd";
import { MenuItem } from "types/menuItems";
import { Link } from "react-router-dom";

const { Sider } = Layout;
const { Item } = Menu;

describe("SideMenu", () => {
  let props: Props;
  const makeComponent = (ctx: Props): ShallowWrapper => {
    props = { ...ctx };

    return shallow(<SideMenu {...props} />);
  };

  it("should render sidebar", () => {
    const wrapper = makeComponent({
      theme: "dark" as Theme,
      menuItems: [
        {
          title: "some-title",
          path: "some-path",
          icon: "some-icon"
        }
      ]
    });

    expect(wrapper.find(Sider)).toHaveLength(1);
    expect(wrapper.find(Menu)).toHaveLength(1);
    expect(wrapper.find(Sider).props()).toHaveProperty("collapsible", true);
    expect(wrapper.find(Sider).props()).toHaveProperty("theme", props.theme);
  });

  it("should render menu items", () => {
    const expectedMenuItems: MenuItem[] = [
      {
        title: "some-title",
        path: "some-path",
        icon: "some-icon"
      },
      {
        title: "some-other-title",
        path: "some-other-path",
        icon: "some-other-icon"
      }
    ];
    const wrapper = makeComponent({
      theme: "dark" as Theme,
      menuItems: expectedMenuItems
    });

    expect(wrapper.find(Item)).toHaveLength(expectedMenuItems.length);
    expect(wrapper.find(Link)).toHaveLength(expectedMenuItems.length);
    expect(wrapper.find(Icon)).toHaveLength(expectedMenuItems.length);
    expect(wrapper.find("span")).toHaveLength(expectedMenuItems.length);
    expectedMenuItems.forEach((expectedMenuItem, index) => {
      expect(
        wrapper
          .find(Link)
          .at(index)
          .props()
      ).toHaveProperty("to", expectedMenuItem.path);

      expect(
        wrapper
          .find(Icon)
          .at(index)
          .props()
      ).toHaveProperty("type", expectedMenuItem.icon);

      expect(
        wrapper
          .find("span")
          .at(index)
          .text()
      ).toEqual(expectedMenuItem.title);
    });
  });
});
