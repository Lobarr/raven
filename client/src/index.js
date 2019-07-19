import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, Switch } from 'react-router-dom'
import { Provider } from 'mobx-react'
import { createBrowserHistory } from 'history'
import { RouterStore, syncHistoryWithStore } from 'mobx-react-router'
import { Login } from './views/index';
import * as serviceWorker from './serviceWorker';
import './index.css'


const browserHistory = createBrowserHistory()
const routingStore = new RouterStore()
const history = syncHistoryWithStore(browserHistory, routingStore)

class Index extends React.Component {
  render() {
    return (
      <Provider store={routingStore}>
        <>
          <Router history={history}>
            <Switch>
              <Route path="/" component={Login} />
            </Switch>
          </Router>
        </>
      </Provider>
    )
  }
}

ReactDOM.render(<Index />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
