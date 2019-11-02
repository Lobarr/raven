import React, { ReactElement } from "react";
import AppState from "types/appState";
import AppStore from "stores/app-store";
import { shallow, ShallowWrapper } from "enzyme";
import BasePage, { Props } from "components/BasePage";
import { SynchronizedHistory, RouterStore } from "mobx-react-router";
import { Layout } from "antd";
import ThemedHeader from "components/ThemedHeader";
import SideMenu from "components/SideMenu";
const { Content } = Layout;

describe("BasePage", () => {
  const makeState = (appStore: AppStore): AppState => {
    const state: AppState = {
      stores: {
        appStore,
        history: {} as SynchronizedHistory,
        routerStore: {} as RouterStore
      }
    };
    return state;
  };
  const makeComponent = (props?: Props): ShallowWrapper => {
    return shallow(<BasePage {...props} />);
  };

  it("should render base page", () => {
    const wrapper = makeComponent();
    expect(wrapper.find(Layout)).toHaveLength(2);
    expect(wrapper.find(ThemedHeader)).toHaveLength(1);
    expect(wrapper.find(SideMenu)).toHaveLength(1);
    expect(wrapper.find(Content)).toHaveLength(1);
  });
});
