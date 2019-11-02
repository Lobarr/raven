import React, { ReactElement } from "react";
import { Layout } from "antd";
import { Theme } from "types/antdProps";
import { Link } from "react-router-dom";

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
      <Link to="/">
        <span
          style={{
            color: theme === "dark" ? "white" : "black",
            fontSize: "2em",
            fontFamily: "Be Vietnam"
          }}
        >
          Raven
        </span>
      </Link>
    </Header>
  );
}
