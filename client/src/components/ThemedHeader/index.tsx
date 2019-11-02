import React, { ReactElement } from "react";
import { Layout } from "antd";
import { Theme } from "types/antdProps";

const { Header } = Layout;

export type Props = {
  theme: Theme;
};

export default function ThemedHeader(props: Props): ReactElement {
  const { theme } = props;
  return (
    <Header
      style={{
        backgroundColor: theme === "light" ? "white" : ""
      }}
    >
      <span
        style={{
          color: theme === "dark" ? "white" : "black",
          fontSize: "2em",
          fontFamily: "Be Vietnam"
        }}
      >
        Raven
      </span>
    </Header>
  );
}
