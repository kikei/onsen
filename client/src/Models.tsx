import assign = require('object-assign')

/** Models **/
export class Onsen {
  public id: number
  public name: string
  public address: string
  public latitude: number
  public longitude: number
  constructor(data: any) {
    this.id        = data['id']
    this.name      = data['name']
    this.address   = data['address']
    this.latitude  = data['latitude']
    this.longitude = data['longitude']
  }
}

export class LatLng {
  public latitude: number
  public longitude: number
  public constructor(latitude: any, longitude: any) {
    this.latitude = latitude
    this.longitude = longitude
  }
  toString(): string {
    return '' + this.latitude + ', ' + this.longitude
  }
}

export interface OnsenEntryState {
  onsenName: string
  candidates: Onsen[]
  selectedOnsen: Onsen
  map: google.maps.Map
  apiGetCandidatesExists: string
  apiGetCandidatesNew: string
  urlFormEdit: string
}
export const InitialState: OnsenEntryState = {
  onsenName: '',
  candidates: null,
  selectedOnsen: null,
  map: null,
  apiGetCandidatesExists: null,
  apiGetCandidatesNew: null,
  urlFormEdit: null
}
// Enable changing initial state from page html.
assign(InitialState, (window as any).initialState)

export enum AddressSelectMethod {
  byText, byMap
}
export interface OnsenAddressState {
  address: string
  mapCenter: LatLng
  location: LatLng
  zoom: number,
  map: google.maps.Map
  selectMethod: AddressSelectMethod
}
export const InitialOnsenAddressState: OnsenAddressState = {
  address: '',
  mapCenter: null,
  location: null,
  zoom: null,
  map: null,
  selectMethod: AddressSelectMethod.byText
}
// Enable changing initial state from page html.
assign(InitialOnsenAddressState, (window as any).initialOnsenAddressState)

/** Actions **/
export interface Action<T> {
  type: ActionType
  payload: T
}

export enum ActionType {
  ChangeOnsenName,
  SubmitOnsenName,
  ReceiveCandidatesExists,
  ReceiveCandidatesNew,
  SelectAddressItem,
  SetMap,
  HideMapModal,

  ChangeAddressText,
  ChangeMapCenter,
  ChangeLocation,
  SwitchAddressSelectMethod,
}
