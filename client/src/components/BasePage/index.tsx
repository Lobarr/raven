import React, { ReactElement, useContext } from 'react';
import { Layout, Menu, Icon } from 'antd';
import { useObserver } from 'mobx-react'
import AppContext from 'stores/app-context'
import { Theme } from 'types/antd-props'

const { Item } = Menu;
const { Sider, Header, Content } = Layout;

type Props = {
  children: ReactElement
}

export default function BasePage(props: Props): ReactElement {
  const { stores } = useContext(AppContext);
  const { appStore } = stores;
  const theme = appStore.theme as Theme;

  return useObserver(() => (
    <Layout>
      <Header
        style={{
          backgroundColor: !appStore.isDarkThemed ? 'white' : ''
        }}
      >
        <span
          style={{
            color: appStore.isDarkThemed ? 'white' : 'black',
            fontSize: '2em',
            fontFamily: 'Be Vietnam'
          }}
        >
          Raven
        </span>
      </Header>
      <Layout>
        <Sider
          collapsible={true}
          theme={theme}
        >
          <Menu
            theme={theme}
          >
            <Item>
              <Icon type="inbox" />
              <span>testing</span>
            </Item>
          </Menu>
        </Sider>
        <Content style={{ backgroundColor: 'pink' }}>
          {props.children}
        </Content>
      </Layout>
    </Layout>
  ))
}
