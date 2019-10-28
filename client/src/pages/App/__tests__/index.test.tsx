import React from 'react';
import { shallow, ShallowWrapper } from 'enzyme';

import App from 'pages/App';
import { BasePage, AppRouter } from 'components';
import AppContext from 'stores/app-context';

describe('App', () => {
  const makeComponent = (): ShallowWrapper => shallow(<App />);

  it('should render component', () => {
    const wrapper = makeComponent();
    expect(wrapper.find(AppRouter)).toHaveLength(1);
    expect(wrapper.find(BasePage)).toHaveLength(1);
    expect(wrapper.find(AppContext.Provider)).toHaveLength(1);
  });
});
