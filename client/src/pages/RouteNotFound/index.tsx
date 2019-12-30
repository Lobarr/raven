import React, { ReactElement } from "react";
import { Layout, Row, Icon } from "antd";
import { useAppContext } from "stores/appContext";
import Error404Light from "assets/404-light.gif";
import Error404Dark from "assets/404-dark.gif";
import { ThemedLayout, ThemedCard } from "components";
import { useObserver } from "mobx-react";

const { Content } = Layout;

export default function RouteNotFound(): ReactElement {
  const { stores } = useAppContext();
  const { routerStore, appStore } = stores;

  const handleClick = (): void => {
    routerStore.push("/");
  };

  return useObserver(() => (
    <ThemedLayout>
      <Content>
        <Row
          type="flex"
          justify="space-around"
          align="middle"
          style={{
            height: "100%"
          }}
        >
          <ThemedCard
            hoverable={true}
            style={{
              width: "40em"
            }}
            title="Page not found!"
            actions={[<Icon type="home" key="home" onClick={handleClick} />]}
          >
            <img
              src={appStore.isDarkThemed ? Error404Dark : Error404Light}
              alt="Error 404, page not found"
              style={{
                width: "100%"
              }}
            />
          </ThemedCard>
        </Row>
      </Content>
    </ThemedLayout>
  ));
}
