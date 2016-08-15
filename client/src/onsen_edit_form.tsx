import * as React from "react"
import * as ReactDOM from "react-dom"
import * as Redux from "redux"
import thunk from 'redux-thunk'
import { Provider, connect } from 'react-redux'
import { OnsenAddressState } from './Models'
import { app } from './OnsenAddressInputReducer'
import { OnsenAddressInput, OnsenAddressProps } from './components/OnsenAddressInput'

const createStoreWithMiddleware =
  Redux.applyMiddleware(thunk as any)(Redux.createStore)

const App = 
  connect((state: OnsenAddressState) => {
    return { state: state }
  })(OnsenAddressInput)

const root = document.getElementById("form-onsen-address-container")
const store = createStoreWithMiddleware(app)

function render() {
  ReactDOM.render(
    <Provider store={store}>
      <App />
    </Provider>,
    root
  )
}
render();
store.subscribe(render);
