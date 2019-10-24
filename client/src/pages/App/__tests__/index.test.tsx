import React from 'react';
import { shallow, ShallowWrapper } from 'enzyme';

import App from 'pages/App';

describe('App', () => {
  const makeComponent = (): ShallowWrapper => shallow(<App />);

  it('should render component', () => {
    const wrapper = makeComponent();
    expect(wrapper.find('h1')).toBeDefined();
  });
});
