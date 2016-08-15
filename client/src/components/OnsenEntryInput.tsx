import { JQuery } from '../JQuery'
import * as React from "react"
import * as Redux from 'redux'
import { ListGroup, Button, FormGroup, ControlLabel, FormControl, Modal } from 'react-bootstrap'
import { Onsen, OnsenEntryState, ActionType } from '../Models'
import { AddressItem } from './AddressItem'
declare var $: {
  ajax(params: any): JQuery
  param(obj: any): string
}

export interface OnsenEntryProps {
  state: OnsenEntryState
  dispatch: Redux.Dispatch<any>
}

export class OnsenEntryInput
extends React.Component<OnsenEntryProps, any> {
  private handleChange(e: any) {
    console.log(e.target.value)
    const onsenName = e.target.value
    console.debug('changeOnsenName name=' + onsenName)
    this.props.dispatch({
        type: ActionType.ChangeOnsenName,
        payload: onsenName
    })
  }
  handleClick(e: React.SyntheticEvent) {
    e.preventDefault()
    console.debug('handleClick')
    this.props.dispatch((dispatch: Redux.Dispatch<any>) => {
      console.debug('function dispatched')
      const onsenName:string = this.props.state.onsenName
      const data: any = {name: onsenName}
      $.ajax({
        url: this.props.state.apiGetCandidatesExists,
        data: data, dataType: 'json',
        success: (msg: any) => {
          console.log(msg);
          dispatch({ type: ActionType.ReceiveCandidatesExists,
                     payload: msg.map((i:any) => new Onsen(i)) })
        },
        error: (e: any) => {
          console.error(e)
        }
      })
      $.ajax({
        url: this.props.state.apiGetCandidatesNew,
        data: data, dataType: 'json',
        success: (msg: any) => {
          console.log(msg);
          dispatch({ type: ActionType.ReceiveCandidatesNew,
                     payload: msg.map((i:any) => new Onsen(i)) })
        },
        error: (e: any) => { console.error(e) }
      })
      dispatch({ type: ActionType.SubmitOnsenName, payload: null })
    })
  }
  selectAddressItem(onsen: Onsen, e: any) {
    console.log('select address item', e, onsen);
    e.preventDefault();
    if (onsen.latitude && onsen.longitude) {
      // already known onsen
      this.props.dispatch({ type: ActionType.SelectAddressItem, 
                            payload: onsen })
    } else {
      // unknown onsen
      this.props.dispatch((dispatch: Redux.Dispatch<any>) => {
        const data: any = {address: onsen.address}
        $.ajax({
          // url: this.props.state.apiGetCandidatesNew,
          url: 'http://127.0.0.1:8000/address/tolatlng',
          data: data, dataType: 'json',
          success: (msg: any) => {
            console.log(msg);
            if (msg.latitude && msg.longitude) {
              // TODO: set properties in reducer!!
              onsen.latitude = msg.latitude
              onsen.longitude = msg.longitude
              dispatch({ type: ActionType.SelectAddressItem, 
                         payload: onsen })
            }
          },
          error: (e: any) => { console.error(e) }
        })
      })
    }
  }
  enterMapModal() {
    console.log('enter map modal');
    const onsen = this.props.state.selectedOnsen
    const mapContainer = document.getElementById('map')
    const map = new google.maps.Map(mapContainer, {
      center: {lat: onsen.latitude, lng: onsen.longitude},
      zoom: 17,
      disableDefaultUI: true,
      draggable: false,
      scrollwheel: false
    })
    this.props.dispatch({ type: ActionType.SetMap, payload: map })

    const latlng = new google.maps.LatLng(onsen.latitude, onsen.longitude);
    const marker = new google.maps.Marker({
      position: latlng,
      icon: "http://maps.google.com/mapfiles/ms/micons/red-pushpin.png"
    });
    marker.setMap(map);
  }
  hideMapModal() {
    console.log('hide map modal')
    this.props.dispatch({ type: ActionType.HideMapModal,
                          payload: null })
  }
  decideAddressItem() {
    console.log('decide address item')
    var onsen = this.props.state.selectedOnsen
    const params: any = {}
    if (onsen.id) {
      params['id'] = onsen.id
    } else {
      params['address'] = onsen.address
      params['name'] = this.props.state.onsenName
    }
    location.href = this.props.state.urlFormEdit + '?' + $.param(params)
  }
  render() {
    const state = this.props.state
    const showModal = state.selectedOnsen != null
    const address = 
       state.selectedOnsen != null ? state.selectedOnsen.address : ''
    const MapModal =
      <Modal bsSize="large" show={showModal}
        onEnter={this.enterMapModal.bind(this)}
        onHide={this.hideMapModal.bind(this)}>
        <Modal.Header closeButton>
          <Modal.Title>Modal heading</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h3>{address}</h3>
            <div className="map-container">
            <div id="map" data-zoom="14" style={{height: '300px'}}></div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button bsStyle="primary"
            onClick={this.decideAddressItem.bind(this)}>
            この住所が近いです
         </Button>
         <Button onClick={this.hideMapModal.bind(this)}>キャンセル</Button>
        </Modal.Footer>
      </Modal>;

    const candidates = state.candidates
    const self = this
    var id = 0
    const Items = (candidates || []).map(function(candidate) {
      return (
        <AddressItem url={'#'} address={candidate.address}
          onClick={self.selectAddressItem.bind(self, candidate)}
          key={id++} />
      );
    });
    const Candidates =
      candidates == null ? <p></p> :
      candidates.length == 0 ? <p>検索中</p> :
      <div>
        <h2>どの住所が一番近いですか？</h2>
        <ListGroup>{Items}</ListGroup>
      </div>;
    return (
      <div className="container">
        <FormGroup>
          <ControlLabel htmlFor="from-onsen-name">
            <h2>温泉・施設名を入力してください</h2>
          </ControlLabel>
          <FormControl type="text" label="from-onsen-name" ref="name"
            placeholder="○○温泉" value={this.props.state.onsenName}
	    onChange={this.handleChange.bind(this)} />
          <Button bsStyle="primary" bsSize="large" block
            onClick={this.handleClick.bind(this)}>送信</Button>
        </FormGroup>
        {Candidates}
        {MapModal}
      </div>
    )
  }
}
