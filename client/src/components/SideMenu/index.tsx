import React, { ReactElement } from "react";
import { Layout, Menu, Icon } from "antd";
import { Theme } from "types/antdProps";
import { Link } from "react-router-dom";
import { MenuItem } from "types/menuItems";

const { Sider } = Layout;
const { Item } = Menu;

export type Props = {
  theme: Theme;
  menuItems: MenuItem[];
};

export default function SideMenu(props: Props): ReactElement {
  const { theme, menuItems } = props;
  return (
    <Sider collapsible={true} theme={theme}>
      <Menu theme={theme}>
        {menuItems.map(({ title, path, icon }, index) => (
          <Item key={index.toString()}>
            <Link to={path}>
              <Icon type={icon} />
              <span>{title}</span>
            </Link>
          </Item>
        ))}
      </Menu>
    </Sider>
  );
}
