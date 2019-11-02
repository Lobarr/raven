import React, { ReactElement } from "react";
import { Layout } from "antd";
import { useAppContext } from "stores/appContext";
import { useObserver } from "mobx-react";
import { DARK_LAYOUT_BACKGROUND_COLOR } from "utils/constants";

export type Props = {
  children?: ReactElement;
};

export default function ThemedLayout(props: Props): ReactElement {
  const { stores } = useAppContext();
  const { appStore } = stores;

  return useObserver(() => (
    <Layout
      style={{
        height: "100%",
        backgroundColor: appStore.isDarkThemed
          ? DARK_LAYOUT_BACKGROUND_COLOR
          : ""
      }}
    >
      {props.children}
    </Layout>
  ));
}
