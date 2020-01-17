import React, { ReactElement, FormEvent } from "react";
import { useObserver } from "mobx-react";
import { ThemedLayout } from "components";
import { Layout, Form, Icon, Input, Button, Row, Typography, notification } from "antd";
import { useAppContext } from "stores/appContext";
import Admin from "services/admin";
import { Redirect } from "react-router";
import { FormComponentProps } from "antd/lib/form/Form";

const { Content } = Layout;
const { Item } = Form;
const { Title } = Typography;


function _Login(props: FormComponentProps): ReactElement {
  const { stores } = useAppContext();
  const { appStore, routerStore } = stores;
  const { form } = props;
  const { getFieldDecorator, validateFields } = form;

  const handleUnauthorizedError = () => {
    notification.error({
      message: "Unauthorized!",
      description: "Username or Password is invalid"
    });
    form.resetFields();
  };

  const handleLogin = async (username: string, password: string) => {
    const response = await Admin.login(username, password);
    const admin = response.data["data"];
    appStore.setAdmin(admin);
    routerStore.push("/");
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    validateFields(async (err, values) => {
      try {
        if (!err) {
          const { username, password } = values;
          await handleLogin(username, password);
        }
      } catch (error) {
        handleUnauthorizedError();
      }
    })
  }

  return useObserver(() => {
    return appStore.isLoggedIn ? (
      <Redirect to="/" />
    ) : (
      <ThemedLayout>
        <Content>
          <Row
            type="flex"
            justify="space-around"
            align="middle"
            style={{
              height: "100%"
            }}
          >
            <Form onSubmit={handleSubmit}>
            <Title level={3} style={{ color: "white" }}>Login</Title>
              <Item>
                {getFieldDecorator("username", {
                  rules: [{ required: true, message: "Please input your username!" }],
                })(
                  <Input
                    prefix={<Icon type="user" style={{ color: "rgba(0,0,0,.25)" }} />}
                    placeholder="Username"
                  />,
                )}
              </Item>
              <Item>
                  {getFieldDecorator("password", {
                    rules: [{ required: true, message: "Please input your Password!" }],
                  })(
                    <Input
                      prefix={<Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />}
                      type="password"
                      placeholder="Password"
                    />,
                  )}
              </Item>
              <Item>
                <Button type="primary" htmlType="submit" className="login-form-button">
                  Log in
                </Button>
              </Item>
            </Form>
          </Row>
        </Content>
      </ThemedLayout>
    );
  });
};



const Login = Form.create({ name: "login" })(_Login)

export default Login;

