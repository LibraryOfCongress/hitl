import React from 'react'
import PropTypes from 'prop-types'

export default class LoadingIndicator extends React.Component {
  static propTypes = {
    fixed: PropTypes.bool
  }

  render() {
    return (
      <span className={'loading-indicator' + (this.props.fixed ? ' is-fixed' : '')}>
        Loading
        <span>•</span>
        <span>•</span>
        <span>•</span>
      </span>
    )
  }
}
