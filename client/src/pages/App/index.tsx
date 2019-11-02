import React, { ReactElement } from "react";
import { Layout } from "antd";
import { BasePage } from "components/";
import AppContext, { initAppState } from "stores/appContext";
import "./index.scss";
import { BrowserRouter } from "react-router-dom";

export default function App(): ReactElement {
  return (
    <BrowserRouter>
      <Layout className="app">
        <AppContext.Provider value={initAppState}>
          <BasePage />
        </AppContext.Provider>
      </Layout>
    </BrowserRouter>
  );
}
