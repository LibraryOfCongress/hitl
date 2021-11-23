import React from 'react'
import marked from '../../lib/marked.min.js'

export default class GenericTask extends React.Component {
  static defaultProps = {
    disabled: false,
    question: '',
    help: '',
    answers: ''
  }

  render() {
    return (
      <div className="workflow-task" disabled={this.props.disabled}>
        <span
          dangerouslySetInnerHTML={{ __html: marked(this.props.question) }}
        />
        <div className="answers">
          {React.Children.map(this.props.answers, answer => {
            return React.cloneElement(answer, {
              className: answer.props.className + ' answer',
              disabled: this.props.badSubject
            })
          })}
        </div>
      </div>
    )
  }
}
