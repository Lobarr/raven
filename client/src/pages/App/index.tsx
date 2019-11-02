import React, { ReactElement } from "react";
import { Layout } from "antd";
import { BasePage } from "components/";
import AppContext, { initAppState } from "stores/app-context";
import "./index.scss";

export default function App(): ReactElement {
  return (
    <Layout className="app">
      <AppContext.Provider value={initAppState}>
        <BasePage />
      </AppContext.Provider>
    </Layout>
  );
}
