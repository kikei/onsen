import { LatLng, OnsenAddressState, InitialOnsenAddressState, AddressSelectMethod, Action, ActionType } from "./Models"
import assign = require('object-assign')

export function app(
  state: OnsenAddressState=InitialOnsenAddressState,
  action: Action<any>): OnsenAddressState {

  switch (action.type) {
  case ActionType.ChangeAddressText:
    return changeAddressText(state, action)
  case ActionType.ChangeMapCenter:
    return changeMapCenter(state, action)
  case ActionType.ChangeLocation:
    return changeLocation(state, action)
  case ActionType.SwitchAddressSelectMethod:
    return switchAddressSelectMethod(state, action)
  case ActionType.SetMap:
    return setMap(state, action)
  default:
    return state
  }
}

function changeAddressText(state: OnsenAddressState,
                           action: Action<string>): OnsenAddressState {
  return assign({}, state, {
    address: action.payload
  })
}
function changeMapCenter(state: OnsenAddressState,
                         action: Action<LatLng>)
: OnsenAddressState {
  console.log('change map center', action.payload)
  return assign({}, state, {
    mapCenter: action.payload
  })
}
function changeLocation(state: OnsenAddressState,
                        action: Action<LatLng>)
: OnsenAddressState {
  console.log('change map center', action.payload)
  return assign({}, state, {
    location: action.payload
  })
}

function switchAddressSelectMethod(state: OnsenAddressState,
                                   action: Action<AddressSelectMethod>)
: OnsenAddressState {
  console.log('switch address select method', action.payload)
  return assign({}, state, {
    selectMethod: action.payload
  })
}
function setMap(state: OnsenAddressState,
                action: Action<google.maps.Map>) {
  console.log('reducer: set map')
  return assign({}, state, {
    map: action.payload
  })
}
