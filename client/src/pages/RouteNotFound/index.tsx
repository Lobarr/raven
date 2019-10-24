import React, { ReactElement, useContext, MouseEvent } from 'react';
import { Layout, Card, Row, Icon } from 'antd';
import { AppContext } from 'stores/';
import Error404 from 'assets/404.gif';

const { Content } = Layout;

export default function RouteNotFound(): ReactElement {
  const { stores } = useContext(AppContext);
  const { routerStore } = stores;

  const handleClick = (): void => {
    routerStore.push('/');
  };

  return (
    <Row
      style={{
        height: '100%'
      }}
    >
      <Layout
        className="routeNotFound"
        style={{
          height: '100%'
        }}
      >
        <Content>
          <Row
            type="flex"
            justify="space-around"
            align="middle"
            style={{
              height: '100%'
            }}
          >
            <Card
              hoverable={true}
              style={{
                width: '40em'
              }}
              title="Page not found!"
              actions={[<Icon type="home" key="home" onClick={handleClick} />]}
            >
              <img
                src={Error404}
                alt="Error 404, page not found"
                style={{
                  width: '100%'
                }}
              />
            </Card>
          </Row>
        </Content>
      </Layout>
    </Row>
  );
}
