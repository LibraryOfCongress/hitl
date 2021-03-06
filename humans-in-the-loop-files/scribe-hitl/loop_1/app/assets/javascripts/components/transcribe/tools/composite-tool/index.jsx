import React from 'react'
import PropTypes from 'prop-types'
import qs from 'query-string'

import DraggableModal from '../../../draggable-modal.jsx'
import SmallButton from '../../../buttons/small-button.jsx'
import HelpButton from '../../../buttons/help-button.jsx'
import BadSubjectButton from '../../../buttons/bad-subject-button.jsx'
import IllegibleSubjectButton from '../../../buttons/illegible-subject-button.jsx'

export default class CompositeTool extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      annotation: this.props.annotation != null ? this.props.annotation : {},
      viewerSize: this.props.viewerSize,
      active_field_key: this.props.task.tool_config.options[0].value
    }
    this.handleChange = this.handleChange.bind(this)
    this.handleCompletedField = this.handleCompletedField.bind(this)
    this.handleFieldFocus = this.handleFieldFocus.bind(this)
    this.commitAnnotation = this.commitAnnotation.bind(this)
  }

  static defaultProps = {
    annotation: {},
    task: null,
    subject: null
  }

  static contextTypes = {
    router: PropTypes.object
  }

  // this can go into a mixin? (common across all transcribe tools)
  getPosition(data) {
    let x, y
    if (data.x == null) {
      return { x: null, y: null }
    }

    const yPad = 20
    switch (data.toolName) {
      case 'rectangleTool':
        x = data.x
        y = parseFloat(data.y) + parseFloat(data.height) + yPad
        break
      case 'horizontalLineTool':
        x = data.x
        y = parseFloat(data.y) + parseFloat(data.height) + yPad
        break
      case 'textRowTool':
        x = data.x
        y = data.yLower + yPad
        break
      default:
        // default for pointTool
        x = data.x
        if (data.y != null) {
          y = data.y + yPad
        }
    }
    if (x == null) {
      x = this.props.subject.width / 2
    }
    if (y == null) {
      y = this.props.subject.height / 2
    }
    return { x, y }
  }

  onViewerResize(size) {
    this.setState({
      viewerSize: size
    })
  }

  handleChange(annotation) {
    this.setState({ annotation })

    this.props.onChange({...annotation})
  } // forward annotation to parent

  // Fires when user hits <enter> in an input
  // If there are more inputs, move focus to next input
  // Otherwise commit annotation (which is default behavior when there's only one input
  handleCompletedField() {
    const field_keys = this.props.task.tool_config.options.map(c => c.value)
    const next_field_key =
      field_keys[field_keys.indexOf(this.state.active_field_key) + 1]

    if (next_field_key != null) {
      return this.setState({ active_field_key: next_field_key }, () => {
        this.forceUpdate()
      })
    } else {
      this.setState({ active_field_key: field_keys[0] }, () => {
        this.commitAnnotation()
      })
    }
  }

  // User moved focus to an input:
  handleFieldFocus(annotation_key) {
    this.setState({ active_field_key: annotation_key })
  }

  // this can go into a mixin? (common across all transcribe tools)
  commitAnnotation() {
    // Clear current annotation so that it doesn't carry over into next task if next task uses same tool
    const ann = this.state.annotation
    this.setState({ annotation: {} }, () => {
      this.props.onComplete(ann)
    })

    if (this.props.transcribeMode === 'page' || this.props.transcribeMode === 'single'
    ) {
      if (this.props.isLastSubject && this.props.task.next_task == null) {
        this.props.returnToMarking()
      }
    } else if (this.props.transcribeMode == 'verify') {
      this.context.router.history.push('/verify')
    }
  }

  // this can go into a mixin? (common across all transcribe tools)
  returnToMarking() {
    this.commitAnnotation()

    // transition back to mark
    this.context.router.history.push(
      '/mark?',
      qs.stringify({
        subject_set_id: this.props.subject.subject_set_id,
        selected_subject_id: this.props.subject.parent_subject_id,
        page: this.props.subjectCurrentPage
      })
    )
  }

  render() {
    const buttons = []
    // TK: buttons.push <PrevButton onClick={=> console.log "Prev button clicked!"} />

    if (this.props.onShowHelp != null) {
      buttons.push(
        <HelpButton onClick={this.props.onShowHelp} key="help-button" />
      )
    }

    if (this.props.onBadSubject != null) {
      buttons.push(
        <BadSubjectButton
          key="bad-subject-button"
          label={`Bad ${this.props.project.term('mark')}`}
          active={this.props.badSubject}
          onClick={this.props.onBadSubject}
        />
      )
    }

    if (this.props.onIllegibleSubject != null) {
      buttons.push(
        <IllegibleSubjectButton
          active={this.props.illegibleSubject}
          onClick={this.props.onIllegibleSubject}
          key="illegible-subject-button"
        />
      )
    }

    let buttonLabel
    if (this.props.task.next_task != null) {
      buttonLabel = 'Continue'
    } else if (this.props.isLastSubject &&
      (this.props.transcribeMode === 'page' ||
        this.props.transcribeMode === 'single')) {
      buttonLabel = 'Return to Marking'
    } else if (this.props.transcribeMode === 'verify') {
      buttonLabel = 'Return to Verify'
    } else {
      buttonLabel = 'Next Entry'
    }

    buttons.push(
      <SmallButton
        label={buttonLabel}
        key="done-button"
        onClick={this.commitAnnotation}
      />
    )

    const { x, y } = this.getPosition(this.props.subject.region)

    return (
      <DraggableModal
        x={x * this.props.scale.horizontal + this.props.scale.offsetX}
        y={y * this.props.scale.vertical + this.props.scale.offsetY}
        buttons={buttons}
        classes="transcribe-tool composite"
      >
        <label>{this.props.task.instruction}</label>
        {(() => {
          const result = []

          for (let index = 0;
            index < this.props.task.tool_config.options.length;
            index++
          ) {
            const sub_tool = this.props.task.tool_config.options[index]
            const ToolComponent = this.props.transcribeTools[sub_tool.tool]
            const annotation_key = sub_tool.value
            const focus = annotation_key === this.state.active_field_key

            result.push(
              <ToolComponent
                key={index}
                task={this.props.task}
                tool_config={sub_tool.tool_config}
                subject={this.props.subject}
                workflow={this.props.workflow}
                standalone={false}
                viewerSize={this.props.viewerSize}
                onChange={this.handleChange}
                onComplete={this.handleCompletedField}
                onInputFocus={this.handleFieldFocus}
                label={sub_tool.label != null ? sub_tool.label : ''}
                focus={focus}
                scale={this.props.scale}
                annotation_key={annotation_key}
                annotation={this.state.annotation}
              />
            )
          }

          return result
        })()}
      </DraggableModal>
    )
  }
}

