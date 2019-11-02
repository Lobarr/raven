import React from "react";
import { ShallowWrapper, shallow } from "enzyme";
import RouteNotFound from "pages/RouteNotFound";
import { ThemedLayout, ThemedCard } from "components";
import Error404Light from "assets/404-light.gif";
import Error404Dark from "assets/404-dark.gif";
import { Layout, Row } from "antd";
import AppState from "types/appState";
import AppStore from "stores/appStore";
import * as AppContext from "stores/appContext";
import { RouterStore, SynchronizedHistory } from "mobx-react-router";

const { Content } = Layout;

describe("RouteNotFoud", () => {
  const makeState = (): AppState => {
    const state: AppState = {
      stores: {
        appStore: new AppStore(),
        routerStore: {} as RouterStore,
        history: {} as SynchronizedHistory
      }
    };

    return state;
  };
  const makeComponent = (): ShallowWrapper => shallow(<RouteNotFound />);

  it("should render", () => {
    const wrapper = makeComponent();

    expect(wrapper.find(Content)).toHaveLength(1);
    expect(wrapper.find(ThemedLayout)).toHaveLength(1);
    expect(wrapper.find(ThemedCard)).toHaveLength(1);
    expect(wrapper.find(Row)).toHaveLength(1);
  });
  it("should handle dark theme", () => {
    const wrapper = makeComponent();

    expect(wrapper.find("img").props()).toHaveProperty("src", Error404Dark);
  });
  it("should handle light theme", () => {
    const state = makeState();
    state.stores.appStore.setTheme("light");
    jest.spyOn(AppContext, "useAppContext").mockReturnValue(state);

    const wrapper = makeComponent();

    expect(wrapper.find("img").props()).toHaveProperty("src", Error404Light);
  });
});
