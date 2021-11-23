import React from 'react'
import PropTypes from 'prop-types'
import GenericTask from './generic.jsx'

const NOOP = Function.prototype

export default class PickOneButtons extends React.Component {
  static defaultProps = {
    task: null,
    annotation: null,
    onChange: NOOP
  }

  static propTypes = {
    task: PropTypes.object.isRequired,
    annotation: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired
  }

  render() {
    const answers =
      Array.from(this.props.task.tool_config.options).map(answer => {
        if (answer._key == null) {
          answer._key = Math.random()
        }
        const checked = answer.value === this.props.annotation.value
        const classes = ['minor-button']
        if (checked) {
          classes.push('active')
        }

        return <button
          key={answer._key}
          type='button'
          value={answer.value}
          onClick={this.onClick}>{answer.label}</button>
      })

    return (
      <GenericTask
        {...Object.assign({ ref: 'inputs' }, this.props, {
          question: this.props.task.instruction,
          answers: answers
        })}
      />
    )
  }

  // Alex Hebing, 2019
  // Change PickOne to buttons (from checkboxes), handle click
  onClick = (e) => {
    this.props.onChange({
      value: e.target.value
    })
    this.forceUpdate()
  }
}
