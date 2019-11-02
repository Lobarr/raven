import React from "react";
import { ShallowWrapper, shallow } from "enzyme";
import ThemedCard, { Props } from "components/ThemedCard";
import AppState from "types/appState";
import * as AppContext from "stores/appContext";
import { RouterStore, SynchronizedHistory } from "mobx-react-router";
import AppStore from "stores/appStore";
import { Card } from "antd";
import { DARK_CARD_HEAD_COLOR, DARK_CARD_BODY_COLOR } from "utils/constants";

describe("ThemedCard", () => {
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
    return shallow(<ThemedCard {...props} />);
  };
  it("should handle light theme", () => {
    const state = makeState();
    state.stores.appStore.setTheme("light");
    jest.spyOn(AppContext, "useAppContext").mockReturnValue(state);

    const wrapper = makeComponent();
    const renderedCard = wrapper.find(Card);

    expect(renderedCard.props()).toHaveProperty("headStyle.color", "black");
    expect(renderedCard.props()).toHaveProperty(
      "headStyle.backgroundColor",
      ""
    );
    expect(renderedCard.props()).toHaveProperty(
      "bodyStyle.backgroundColor",
      ""
    );
  });
  it("should handle dark theme", () => {
    jest.spyOn(AppContext, "useAppContext").mockReturnValue(makeState());

    const wrapper = makeComponent();
    const renderedCard = wrapper.find(Card);

    expect(renderedCard.props()).toHaveProperty("headStyle.color", "white");
    expect(renderedCard.props()).toHaveProperty(
      "headStyle.backgroundColor",
      DARK_CARD_HEAD_COLOR
    );
    expect(renderedCard.props()).toHaveProperty(
      "bodyStyle.backgroundColor",
      DARK_CARD_BODY_COLOR
    );
  });
});
