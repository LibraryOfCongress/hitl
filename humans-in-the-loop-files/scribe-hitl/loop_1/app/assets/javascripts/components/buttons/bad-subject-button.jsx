import React from 'react'
import PropTypes from 'prop-types'
import SmallButton from './small-button.jsx'

export default class BadSubjectButton extends React.Component {
  static propTypes = {
    active: PropTypes.bool,
    className: PropTypes.string,
    label: PropTypes.string,
    onClick: PropTypes.func
  }
  render() {
    const label = this.props.label || (this.props.active
      ? 'Bad Subject'
      : 'Bad Subject?')

    const additional_classes = []
    if (this.props.active) {
      additional_classes.push('toggled')
    }
    if (this.props.className != null) {
      additional_classes.push(this.props.className)
    }
    return (
      <SmallButton
        key="bad-subject-button"
        label={label}
        onClick={this.props.onClick}
        className={`bad-subject ghost toggle-button ${additional_classes.join(' ')}`}
      />
    )
  }
}
