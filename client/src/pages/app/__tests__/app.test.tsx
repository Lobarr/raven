import React from 'react';
import { shallow } from 'enzyme';

import App from 'pages/app/app';

describe('App', () => {
  const makeComponent = () => {
    return shallow(<App />);
  };
  it('should render component', () => {
    const wrapper = makeComponent();
    expect(wrapper.find('h1')).toBeDefined();
  });
});
