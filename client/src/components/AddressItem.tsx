import * as React from "react"
import { ListGroupItem, Button } from 'react-bootstrap'
import { Onsen } from '../Models'

export interface AddressItemProps {
  url: string
  address: string
  onClick: any
}

export class AddressItem
extends React.Component<AddressItemProps, any> {
  render() {
    return (
      <ListGroupItem href={this.props.url}
        onClick={this.props.onClick}>
        {this.props.address}
      </ListGroupItem>
    )
  }
}
