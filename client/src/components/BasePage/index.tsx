import React, { ReactElement, useContext } from "react";
import { Layout } from "antd";
import { useObserver } from "mobx-react";
import AppContext from "stores/app-context";
import ThemedHeader from "components/ThemedHeader";
import SideMenu from "components/SideMenu";
import routes from "config/routes";
import menuItems from "config/menuItems";
import AppRouter from "components/AppRouter";
import { BrowserRouter } from "react-router-dom";

const { Content } = Layout;

export type Props = {
  children?: ReactElement;
};

export default function BasePage(props: Props): ReactElement {
  const { stores } = useContext(AppContext);
  const { appStore } = stores;
  const { theme } = appStore;

  return useObserver(() => (
    <BrowserRouter>
      <Layout>
        <ThemedHeader theme={theme} />
        <Layout>
          <SideMenu theme={theme} menuItems={menuItems} />
          <Content>
            <AppRouter routes={routes} />
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  ));
}
