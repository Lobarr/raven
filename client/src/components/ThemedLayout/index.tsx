import React, { ReactElement, useContext } from "react";
import { Layout } from "antd";
import AppContext from "stores/app-context";
import { useObserver } from "mobx-react";
import { DARK_LAYOUT_BACKGROUND_COLOR } from "utils/constants";

type Props = {
  children?: ReactElement
}

export default function ThemedLayout(props: Props): ReactElement {
  const { stores } = useContext(AppContext);
  const { appStore } = stores;

  return useObserver(() => (
    <Layout
      style={{
        height: "100%",
        backgroundColor: appStore.isDarkThemed ? DARK_LAYOUT_BACKGROUND_COLOR : ""
      }}
    >
      {props.children}
    </Layout>
  ))
}
