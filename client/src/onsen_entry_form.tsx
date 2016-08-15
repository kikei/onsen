import * as React from "react"
import * as ReactDOM from "react-dom"
import * as Redux from "redux"
import thunk from 'redux-thunk'
import { Provider, connect } from 'react-redux'
import { OnsenEntryState } from './Models'
import { app } from './Reducer'
import { OnsenEntryInput, OnsenEntryProps } from './components/OnsenEntryInput'

const createStoreWithMiddleware =
  Redux.applyMiddleware(thunk as any)(Redux.createStore)

const App = 
  connect((state: OnsenEntryState) => {
    return { state: state }
  })(OnsenEntryInput)

const root = document.getElementById("example")
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
