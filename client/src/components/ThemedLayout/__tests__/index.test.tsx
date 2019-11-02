import React from "react";
import { ShallowWrapper, shallow } from "enzyme";
import ThemedLayout, { Props } from "components/ThemedLayout";
import AppState from "types/appState";
import AppStore from "stores/appStore";
import * as AppContext from "stores/appContext";
import { RouterStore, SynchronizedHistory } from "mobx-react-router";
import { Layout } from "antd";
import { DARK_LAYOUT_BACKGROUND_COLOR } from "utils/constants";

describe("ThemedLayout", () => {
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
  const makeComponent = (props: Props = {} as Props): ShallowWrapper => {
    return shallow(<ThemedLayout {...props} />);
  };

  it("should handle light theme", () => {
    const state = makeState();
    state.stores.appStore.setTheme("light");
    jest.spyOn(AppContext, "useAppContext").mockReturnValue(state);

    const wrapper = makeComponent();

    expect(wrapper.find(Layout).props()).toHaveProperty(
      "style.backgroundColor",
      ""
    );
  });
  it("should handle dark theme", () => {
    jest.spyOn(AppContext, "useAppContext").mockReturnValue(makeState());

    const wrapper = makeComponent();

    expect(wrapper.find(Layout).props()).toHaveProperty(
      "style.backgroundColor",
      DARK_LAYOUT_BACKGROUND_COLOR
    );
  });
});
