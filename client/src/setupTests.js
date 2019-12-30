import { configure } from 'enzyme';
import EnzymeAdapter16 from 'enzyme-adapter-react-16';
import JestLocalStorageMock from 'jest-localstorage-mock';

configure({
  adapter: new EnzymeAdapter16()
});
