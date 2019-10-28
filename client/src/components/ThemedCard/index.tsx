import React, { ReactElement, ReactNode, useContext } from 'react';
import { Card } from 'antd';
import AppContext from 'stores/app-context';
import { useObserver } from 'mobx-react';
import { DARK_CARD_HEAD_COLOR, DARK_CARD_BODY_COLOR } from 'utils/constants';

type Props = {
  actions?: Array<ReactNode>;
  hoverable?: boolean;
  loading?: boolean;
  size?: "default" | "small";
  title?: string | ReactNode;
  style?: object;
  children?: ReactElement;
}

export default function ThemedCard(props: Props): ReactElement {
  const { stores } = useContext(AppContext);
  const { appStore } = stores;

  return useObserver(() => (
    <Card
      bordered={false}
      headStyle={{
        backgroundColor: appStore.isDarkThemed ? DARK_CARD_HEAD_COLOR : '',
        color: appStore.isDarkThemed ? "white" : "black"
      }}
      bodyStyle={{
        backgroundColor: appStore.isDarkThemed ? DARK_CARD_BODY_COLOR : '',
      }}
      {...props}
    >
      {props.children}
    </Card>
  ));
}
