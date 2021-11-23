var _this = this

/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS208: Avoid top-level this
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */


import React from 'react'

// IMPORTANT!
window.React = React

import createReactClass from 'create-react-class'
import { getCsrfHeaders } from '../lib/csrf'
const FavouriteButton = createReactClass({
  displayname: 'FavouriteButton',

  getInitialState: () => {
    return {
      favourite: _this.props.subject.user_favourite,
      loading: false
    }
  },

  add_favourite(e) {
    e.preventDefault()

    this.setState({
      loading: true
    })

    return $.ajax({
      url: `/subjects/${this.props.subject.id}/favourite`,
      method: 'post',
      headers: getCsrfHeaders(),
      success: () => {
        return this.setState({
          loading: false,
          favourite: true
        })
      }
    })
  },

  remove_favourite(e) {
    e.preventDefault()
    return $.ajax({
      url: `/subjects/${this.props.subject.id}/unfavourite`,
      method: 'post',
      headers: getCsrfHeaders(),
      success: () => {
        return this.setState({
          loading: false,
          favourite: false
        })
      }
    })
  },

  render() {
    if (this.state.loading) {
      return <a className="favourite_button">Loading</a>
    } else if (this.state.favourite) {
      return (
        <a
          herf="#"
          onClick={this.remove_favourite}
          className="favourite_button"
        >
          Unfavourite
        </a>
      )
    } else {
      return (
        <a href="#" onClick={this.add_favourite} className="favourite_button">
          Favourite
        </a>
      )
    }
  }
})

export default FavouriteButton
