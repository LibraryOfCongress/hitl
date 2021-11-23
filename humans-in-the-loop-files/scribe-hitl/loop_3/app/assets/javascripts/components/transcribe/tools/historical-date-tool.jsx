import React from 'react'
import ReactDOM from 'react-dom'
import { DateAnnotatorComponent } from 'historical-dates-ui'
import marked from '../../../lib/marked.min.js'
import DraggableModal from '../../draggable-modal.jsx'
import SmallButton from '../../buttons/small-button.jsx'
import HelpButton from '../../buttons/help-button.jsx'
import BadSubjectButton from '../../buttons/bad-subject-button.jsx'
import IllegibleSubjectButton from '../../buttons/illegible-subject-button.jsx'

export default class HistoricalDateTool extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      annotation: props.annotation != null ? { ...props.annotation } : {},
      viewerSize: props.viewerSize
    }
  }

  // this can go into a mixin? (common across all transcribe tools)
  getPosition(data) {
    let x, y
    if (data.x == null) {
      return { x: null, y: null }
    }

    const yPad = 20
    x = data.x
    y = parseFloat(data.y) + parseFloat(data.height) + yPad

    if (x == null) {
      x = this.props.subject.width / 2
    }
    if (y == null) {
      y = this.props.subject.height / 2
    }
    return { x, y }
  }

  toolConfig() {
    return this.props.tool_config != null
      ? this.props.tool_config
      : this.props.task.tool_config
  }

  // Set focus on input:
  focus() {
    if ($(this.refs.toolContent).find(':focus').length) {
      // don't switch focus within the tool
      return
    }
    const el = $(
      this.refs.input0 != null ? ReactDOM.findDOMNode(this.refs.input0) : undefined
    )
    if (el != null && el.length) {
      el.focus()
    }
  }

  componentWillReceiveProps(new_props) {
    // PB: Note this func is defined principally to allow a parent composite-tool
    // to set focus on a child tool via props but this consistently fails to
    // actually set focus - probably because the el.focus() call is made right
    // before an onkeyup event or something, which quietly reverses it.
    if (new_props.focus) {
      this.focus()
    }

    // Required to ensure tool has cleared annotation even if tool doesn't unmount between tasks:
    this.setState({
      annotation: new_props.annotation != null ? { ...new_props.annotation } : {},
      viewerSize: new_props.viewerSize
    })
  }

  shouldComponentUpdate() {
    return true
  }

  componentDidMount() {
    if (this.props.focus) {
      this.focus()
    }
  }

  componentDidUpdate() {
    if (this.props.focus) {
      this.focus()
    }
  }

  // Expects size hash with:
  //   w: [viewer width]
  //   h: [viewer height]
  //   scale:
  //     horizontal: [horiz scaling of image to fit within above vals]
  //     vertical:   [vert scaling of image..]
  onViewerResize(size) {
    this.setState({
      viewerSize: size
    })
  }

  // this can go into a mixin? (common across all transcribe tools)
  // NOTE: doesn't get called unless @props.standalone is true
  commitAnnotation() {
    const ann = this.state.annotation
    const value = ann[this.fieldKey()]
    function dateToPlainObject(date, key) {
      if (!date[key]) {
        // no value defined
        return
      }
      let plain = {
        year: date[key].year,
        month: date[key].month,
        day: date[key].day
      }
      if (plain.year === undefined) plain.year = '??'
      if (plain.month === undefined) plain.month = '??'
      if (plain.day === undefined) plain.day = '??'

      date[key] = plain
    }
    if (value) {
      dateToPlainObject(value, 'date')
      dateToPlainObject(value, 'gregorianDate')
      dateToPlainObject(value, 'julianDate')
    }
    this.props.onComplete({ ...ann })

    if (
      this.props.transcribeMode === 'page' ||
      this.props.transcribeMode === 'single'
    ) {
      if (this.props.isLastSubject && this.props.task.next_task == null) {
        this.props.returnToMarking()
      }
    }
  }

  // Get key to use in annotations hash (i.e. typically 'value', unless included in composite tool)
  fieldKey() {
    return this.props.standalone ? 'value' : this.props.annotation_key
  }

  updateValue(val) {
    this.setState((state) => {
      const newAnnotation = state.annotation
      const currentAnnotation = newAnnotation[this.fieldKey()]
      // skip if it is still empty: there is some weird issue causing
      // this tool to linger after advancing to the next task:
      // e.g. the next task is transcribing a text,
      // this is called and transform the empty text to some
      // JSON-object causing the entry field to contain [object Object]
      if (currentAnnotation || val.text) {
        // merge new text/date into annotation
        newAnnotation[this.fieldKey()] =
          Object.assign(newAnnotation[this.fieldKey()] || {}, val)

        // if composite-tool is used, this will be a callback to CompositeTool::handleChange()
        // otherwise, it'll be a callback to Transcribe::handleDataFromTool()
        this.props.onChange({ ...newAnnotation })
      }
      return { annotation: newAnnotation }
    })
  } // report updated annotation to parent

  handleChangeDate(e) {
    this.updateValue({ ...e })
  }

  handleChangeText(e) {
    this.updateValue({ text: e.target.value })
  }

  handleKeyDown(e) {
    this.handleChangeText(e) // notifies the date entry component

    if ([13].indexOf(e.keyCode) >= 0 && !e.shiftKey) {
      // ENTER
      this.commitAnnotation()
    }
  }

  handleBadMark() {
    const newAnnotation = []
    return newAnnotation['low_quality_subject']
  }

  render() {
    let label
    if (this.props.loading) {
      return null
    } // hide transcribe tool while loading image

    let val = this.state.annotation[this.fieldKey()]
      || { text: '', date: null, type: undefined }
    if (!this.props.standalone) {
      label = this.props.label != null ? this.props.label : ''
      if (Array.isArray(label)) {
        label = label[0]
      }
    } else {
      label = this.props.task.instruction
    }

    const ref = this.props.ref || 'input0'

    // Grab examples either from examples in top level of task or (for composite tool) inside this field's option hash:
    const examples =
      this.props.task.examples != null
        ? this.props.task.examples
        : Array.from(
          this.props.task.tool_config &&
          this.props.task.tool_config.options ||
          []
        ).filter(t => t.value === this.props.annotation_key).map(x => x.examples)
    // create component input field(s)
    let toolContent = (
      <div className="input-field active" ref="toolContent">
        <label dangerouslySetInnerHTML={{ __html: marked(label) }} />
        {examples && (
          <ul className="task-examples">
            {Array.from(examples).map((ex, i) => (
              <li key={i}>{ex}</li>
            ))}
          </ul>
        )}
        <input {...Object.assign({ type: 'text', value: val.text }, {
          ref,
          key: `${this.props.task.key}.${this.props.annotation_key}`,
          'data-task_key': this.props.task.key,
          onKeyDown: this.handleKeyDown.bind(this),
          onChange: this.handleChangeText.bind(this),
          onFocus: () =>
            typeof this.props.onInputFocus === 'function'
              ? this.props.onInputFocus(this.props.annotation_key)
              : undefined,
          value: val.text,
          disabled: this.props.badSubject
        })} />
        <div style={{ display: !val.text ? 'none' : '' }}>
          <DateAnnotatorComponent {...Object.assign({ onChange: this.handleChangeDate.bind(this) }, { text: val.text, type: val.type })} />
        </div>
      </div>
    )

    if (this.props.standalone) {
      // 'standalone' true if component handles own mouse events

      const buttons = []

      if (this.props.onShowHelp != null) {
        buttons.push(
          <HelpButton key="help-button" onClick={this.props.onShowHelp} />
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
            key="illegal-subject-button"
            active={this.props.illegibleSubject}
            onClick={this.props.onIllegibleSubject}
          />
        )
      }

      const buttonLabel =
        this.props.task.next_task != null
          ? 'Continue'
          : this.props.isLastSubject &&
            (this.props.transcribeMode === 'page' ||
              this.props.transcribeMode === 'single')
            ? 'Return to Marking'
            : 'Next Entry'

      buttons.push(
        <SmallButton
          label={buttonLabel}
          key="done-button"
          onClick={this.commitAnnotation.bind(this)}
        />
      )

      const { x, y } = this.getPosition(this.props.subject.region)

      toolContent = (
        <DraggableModal
          x={x * this.props.scale.horizontal + this.props.scale.offsetX}
          y={y * this.props.scale.vertical + this.props.scale.offsetY}
          buttons={buttons}
          classes="transcribe-tool historical-date-tool"
        >
          {toolContent}
        </DraggableModal>
      )
    }

    return <div>{toolContent}</div>
  }

  static defaultProps = {
    annotation: {},
    annotation_key: null,
    task: null,
    subject: null,
    standalone: true,
    focus: true,
    inputType: 'text'
  }
}
