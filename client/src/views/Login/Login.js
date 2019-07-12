import React from 'react';
import { Header, HeaderName, HeaderGlobalAction, HeaderGlobalBar, HeaderPanel} from 'carbon-components-react/lib/components/UIShell'
import './Login.css';

function Login() {
  return (
    <div className="App">
      <Header aria-label="IBM Platform Name">
        <HeaderName href="#" prefix="IBM">
          [Raven]
        </HeaderName>
        <HeaderGlobalBar>
         
        </HeaderGlobalBar>
        <HeaderPanel expanded />
      </Header>
    </div>
  );
}

export default Login;
