import { JQuery } from '../JQuery'
import * as React from "react"
import * as Redux from 'redux'
import { ListGroup, Button, FormGroup, ControlLabel, FormControl, Modal } from 'react-bootstrap'
import { OnsenAddressState, LatLng, ActionType, AddressSelectMethod } from '../Models'
declare var $: {
  ajax(params: any): JQuery
  param(obj: any): string
}

export interface OnsenAddressProps {
  state: OnsenAddressState
  dispatch: Redux.Dispatch<any>
}

export class OnsenAddressInput
extends React.Component<OnsenAddressProps, any> {
  handleChange(e: any) {
    console.log(e.target.value)
    const address = e.target.value
    console.debug('chane address address =' + address)
    this.props.dispatch({ type: ActionType.ChangeAddressText,
                          payload: address })
  }
  selectByMap(e: any) {
    e.preventDefault();
    const state = this.props.state
    const address = state.address
    console.log('select by map button clicked, address =', address)
    if (!address) {
      // use default location as address is not given
      const latitude = 37.4
      const longitude = 141.0
      const latlng = {latitude: latitude, longitude: longitude }
      this.props.dispatch({ type: ActionType.ChangeMapCenter,
                            payload: latlng })
      this.props.dispatch({ type: ActionType.SwitchAddressSelectMethod,
                            payload: AddressSelectMethod.byMap })
    } else {
      this.props.dispatch((dispatch: Redux.Dispatch<any>) => {
        const data: {address: string} = {address: address}
        $.ajax({
          // url: this.props.state.apiGetCandidatesNew,
          url: '/address/tolatlng',
          data: data, dataType: 'json',
          success: (msg: any) => {
            console.log(msg);
            if (msg.latitude && msg.longitude) {
              dispatch({ type: ActionType.ChangeMapCenter,
                         payload: msg })
              this.props.dispatch({ type: ActionType.SwitchAddressSelectMethod,
                                    payload: AddressSelectMethod.byMap })
            }
          },
          error: (e: any) => { console.error(e) }
        })
      })
    }
  }
  enterMapModal() {
    console.log('enter map modal')
    const state = this.props.state
    const mapContainer = document.getElementById('map')
    const map = new google.maps.Map(mapContainer, {
      center: {lat: state.mapCenter.latitude, lng: state.mapCenter.longitude},
      zoom: 17,
    })
    this.props.dispatch((dispatch: Redux.Dispatch<any>) => {
      google.maps.event.addListener(map, 'center_changed',
                                    (evt: google.maps.Map) => {
        const center = map.getCenter()
        console.log('center_changed center = ', center)
        dispatch({ type: ActionType.ChangeMapCenter,
                   payload: {latitude: center.lat(), longitude: center.lng() } })
      })
      var marker: google.maps.Marker = null
      google.maps.event.addListener(map, 'click',
        (evt: google.maps.MouseEvent) => {
          if (!marker) {
            marker = new google.maps.Marker({
              position: evt.latLng,
              icon: "http://maps.google.com/mapfiles/ms/micons/red-pushpin.png"
            });
            marker.setMap(map);
          } else {
            marker.setPosition(evt.latLng)
          }
          const latitude: number = evt.latLng.lat()
          const longitude: number = evt.latLng.lng()
          const location: LatLng = new LatLng(latitude, longitude)
          dispatch({ type: ActionType.ChangeLocation, payload: location })
        }
      )
    })
    this.props.dispatch({ type: ActionType.SetMap, payload: map })
  }
  registerAddress() {
    console.log('register address')
    const latitude = this.props.state.location.latitude
    const longitude = this.props.state.location.longitude
    this.props.dispatch((dispatch: Redux.Dispatch<any>) => {
      const data: {latitude: number, longitude: number} =
        {latitude: latitude, longitude: longitude}
      $.ajax({
        // url: this.props.state.apiGetCandidatesNew,
        url: '/address/bylatlng',
        data: data, dataType: 'json',
        success: (msg: string) => {
          console.log(msg);
          if (msg) {
            dispatch({ type: ActionType.ChangeAddressText,
                       payload: msg })
            dispatch({ type: ActionType.SwitchAddressSelectMethod,
                       payload: AddressSelectMethod.byText })
          }
        },
        error: (e: any) => { console.error(e) }
      })
    })
  }
  hideMapModal() {
    console.log('hide map modal')
    this.props.dispatch({ type: ActionType.SwitchAddressSelectMethod,
                          payload: AddressSelectMethod.byText })
  }
  render() {
    const state = this.props.state
    const showModal = state.selectMethod == AddressSelectMethod.byMap
    const h3 = state.location ?
      state.location.toString() : '温泉の位置をクリックして下さい'
    const MapModal =
      <Modal bsSize="large" show={showModal}
        onEnter={this.enterMapModal.bind(this)}
        onHide={this.hideMapModal.bind(this)}>
        <Modal.Header closeButton>
          <Modal.Title>地図から入力する</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h3>{h3}</h3>
          <div className="map-container">
            <div id="map" data-zoom="14" style={{height: '300px'}}></div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={this.registerAddress.bind(this)}>
            ここに登録する
          </Button>
          <Button onClick={this.hideMapModal.bind(this)}>キャンセル</Button>
        </Modal.Footer>
      </Modal>
    return (
      <div>
        <FormControl type="text" name="address" label="from-onsen-address" ref="address"
          placeholder="○○県○○市○○町" value={state.address}
          onChange={this.handleChange.bind(this)} />
        <Button bsStyle="link" bsSize="small" 
          onClick={this.selectByMap.bind(this)}>地図から入力する</Button>
        {MapModal}
      </div>
    )
  }
}
