import React, { ReactElement } from "react";
import { Layout } from "antd";
import { useObserver } from "mobx-react";
import { useAppContext } from "stores/appContext";
import ThemedHeader from "components/ThemedHeader";
import SideMenu from "components/SideMenu";
import routes from "config/routes";
import menuItems from "config/menuItems";
import AppRouter from "components/AppRouter";

const { Content } = Layout;

export default function BasePage(): ReactElement {
  const { stores } = useAppContext();
  const { appStore } = stores;
  const { theme } = appStore;

  return useObserver(() => (
    <Layout>
      <ThemedHeader theme={theme} />
      <Layout>
        <SideMenu theme={theme} menuItems={menuItems} />
        <Content>
          <AppRouter routes={routes} />
        </Content>
      </Layout>
    </Layout>
  ));
}
