import { Onsen, OnsenEntryState, InitialState, Action, ActionType } from "./Models"
import assign = require('object-assign')

export function app(state: OnsenEntryState = InitialState,
                    action: Action<any>): OnsenEntryState
{
  switch (action.type) {
  case ActionType.ChangeOnsenName:
    return changeOnsenName(state, action)
  case ActionType.SubmitOnsenName:
    return submitOnsenName(state, action)
  case ActionType.ReceiveCandidatesExists:
    return receiveCandidatesExists(state, action)
  case ActionType.ReceiveCandidatesNew:
    return receiveCandidatesNew(state, action)
  case ActionType.SelectAddressItem:
    return selectAddressItem(state, action)
  case ActionType.HideMapModal:
    return hideMapModal(state, action)
  case ActionType.SetMap:
    return setMap(state, action)
  default:
    return state
  }
}

function changeOnsenName(state: OnsenEntryState,
                         action: Action<string>): OnsenEntryState {
  return assign({}, state, {
    onsenName: action.payload
  } as OnsenEntryState)
}
function submitOnsenName(state: OnsenEntryState,
                         action: Action<void>): OnsenEntryState {
  console.log('reducer: search onsen by name')
  return assign({}, state, {
    candidates: null
  })
}
function receiveCandidatesExists(state: OnsenEntryState,
                                 action: Action<Onsen[]>): OnsenEntryState {
  console.log('reducer: receive candidates exists')
  console.log(action.payload)
  return assign({}, state, {                           
    candidates: 
      state.candidates ?
        state.candidates.concat(action.payload) : action.payload
  })
}
function receiveCandidatesNew(state: OnsenEntryState,
                              action: Action<Onsen[]>): OnsenEntryState {
  console.log('reducer: receive candidates new')
  console.log(action.payload)
  return assign({}, state, {                           
    candidates: 
      state.candidates ?
        state.candidates.concat(action.payload) : action.payload
  })
}
function selectAddressItem(state: OnsenEntryState,
                           action: Action<Onsen>): OnsenEntryState {
  console.log('reducer: select address item')
  console.log(action.payload)
  return assign({}, state, {
    selectedOnsen: action.payload
  })
}
function hideMapModal(state: OnsenEntryState,
                      action: Action<void>): OnsenEntryState {
  console.log('reducer: hide map modal')
  return assign({}, state, {
    selectedOnsen: null
  })
}
function setMap(state: OnsenEntryState,
                action: Action<google.maps.Map>) {
  console.log('reducer: set map')
  return assign({}, state, {
    map: action.payload
  })
}
