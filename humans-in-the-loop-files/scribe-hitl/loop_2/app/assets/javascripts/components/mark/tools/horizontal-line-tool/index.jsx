import React from 'react'
import PropTypes from 'prop-types'
import Draggable from '../../../../lib/draggable.jsx'
import DeleteButton from '../../../../components/buttons/delete-mark.jsx'
import MarkButtonMixin from '../../../../lib/mark-button-mixin.jsx'
import MarkLabel from '../mark-label.jsx'

const STROKE_WIDTH = 10
const DEFAULT_WIDTH = 1000
const DELETE_BUTTON_DISTANCE_X = 12
const DELETE_BUTTON_DISTANCE_Y = -18
/**
 * Prevent new lines being placed which are too near other lines
 * (in case people miss click an existing line)
 */
const OVERLAP_THRESHOLD = 100

@MarkButtonMixin
export default class HorizontalLineTool extends React.Component {
  static propTypes = {
    // key:  PropTypes.number.isRequired
    mark: PropTypes.object.isRequired,
    disabled: PropTypes.bool,
    isTranscribable: PropTypes.bool,
    interim: PropTypes.bool,
    selected: PropTypes.bool,
    xScale: PropTypes.number,
    yScale: PropTypes.number,
    onChange: PropTypes.func,
    onDestroy: PropTypes.func,
    onSelect: PropTypes.func,
    sizeRect: PropTypes.object
  }
  initCoords = null;

  static defaultValues({ y }, sizeRect) {
    return {
      x: 0,
      y: y,
      width: sizeRect && sizeRect.attributes && sizeRect.attributes.width && sizeRect.attributes.width.value || DEFAULT_WIDTH,
      height: 0
    }
  }

  static initStart({ x, y }) {
    x = 0
    this.initCoords = { x, y }
    return { x, y }
  }

  static initMove(cursor) {
    return { y: cursor.y }
  }

  static initValid(mark, marks) {
    const candidates = marks.filter(m => !m.user_has_deleted &&
      m.toolName === mark.toolName &&
      m.label === mark.label)

    for (let c of candidates) {
      if (Math.abs(mark.y - c.y) < OVERLAP_THRESHOLD) {
        return false
      }
    }

    return true
  }

  /**
   * This callback is called on mouseup to override mark properties (e.g. if too small)
   */
  static initRelease(coords, mark) {
    mark.width = Math.max(mark.width, DEFAULT_WIDTH)
    mark.height = STROKE_WIDTH
    return mark
  }

  constructor(props) {
    super(props)
    let mark = this.props.mark
    if (mark.status == null) {
      mark.status = 'mark'
    }

    this.state = {
      mark: mark,
      buttonDisabled: false,
      lockTool: false
    }
  }

  handleMainDrag(e, d) {
    if (this.state.locked) {
      return
    }
    if (this.props.disabled) {
      return
    }
    this.props.mark.x += d.x / this.props.xScale
    this.props.mark.y += d.y / this.props.yScale
    this.assertBounds()
    return this.props.onChange(e)
  }

  assertBounds() {
    this.props.mark.x = 0

    this.props.mark.y = Math.min(this.props.sizeRect.attributes.height.value - this.props.mark.height, this.props.mark.y)
    this.props.mark.y = Math.max(0, this.props.mark.y)

    this.props.mark.width = this.props.sizeRect.attributes.width.value
    this.props.mark.height = STROKE_WIDTH
  }

  validVert(y, h) {
    return y >= 0 && y + h <= this.props.sizeRect.attributes.height.value
  }

  validHoriz(x, w) {
    return x >= 0 && x + w <= this.props.sizeRect.attributes.width.value
  }

  getDeleteButtonPosition() {
    let points = [this.props.mark.x + this.props.mark.width, this.props.mark.y],
      x = points[0] + DELETE_BUTTON_DISTANCE_X / this.props.xScale,
      y = points[1] + DELETE_BUTTON_DISTANCE_Y / this.props.yScale
    x = Math.min(x, this.props.sizeRect.attributes.width.value - 15 / this.props.xScale)
    y = Math.max(y, 15 / this.props.yScale)
    return { x, y }
  }

  getMarkButtonPosition() {
    let points = [this.props.mark.x + this.props.mark.width, this.props.mark.y + this.props.mark.height]
    return {
      x: Math.min(points[0], this.props.sizeRect.attributes.width.value - 40 / this.props.xScale),
      y: Math.min(points[1] + 20 / this.props.yScale, this.props.sizeRect.attributes.height.value - 15 / this.props.yScale)
    }
  }

  handleMouseDown() {
    this.props.onSelect(this.props.mark)
  }

  normalizeMark() {
    if (this.props.mark.width < 0) {
      this.props.mark.x += this.props.mark.width
      this.props.mark.width *= -1
    }
    if (this.props.mark.height < 0) {
      this.props.mark.y += this.props.mark.height
      this.props.mark.height *= -1
    }
    return this.props.onChange()
  }

  render() {
    let classes = []
    if (this.props.isTranscribable) {
      classes.push('transcribable')
    }
    if (this.props.interim) {
      classes.push('interim')
    }
    classes.push(this.props.disabled ? 'committed' : 'uncommitted')
    if (this.checkLocation()) {
      classes.push('transcribing')
    }

    let x1 = this.props.mark.x,
      width = this.props.mark.width,
      x2 = x1 + width,
      y1 = this.props.mark.y,
      height = STROKE_WIDTH,
      y2 = y1 + height,

      x = this.props.mark.x,
      y = this.props.mark.y,

      scale = (this.props.xScale + this.props.yScale) / 2,
      
      points = [
        [x1, y1].join(','),
        [x2, y1].join(','),
        [x2, y2].join(','),
        [x1, y2].join(','),
        [x1, y1].join(',')
      ].join('\n')

    let deleteButtonPos
    return (
      <g
        data-tool={this}
        onMouseDown={this.props.onSelect}
        title={this.props.mark.label}
      >
        <g
          className={`horizontal-line-tool${this.props.disabled ? ' locked' : ''}`}
        >

          <Draggable onDrag={this.handleMainDrag.bind(this)} >
            <g className={`tool-shape ${classes.join(' ')}`}
              key={points}>
              <filter id="dropShadow"
                dangerouslySetInnerHTML={{
                  __html: `
                  <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
                  <feOffset dx="2" dy="4" />
                  <feMerge>
                    <feMergeNode />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
              `
                }} />
              <rect fill={this.props.mark.color || 'gray'}
                x={x}
                y={y}
                width={width}
                height={height}
                filter={this.props.selected ? 'url(#dropShadow)' : 'none'}
              />
              <MarkLabel scale={scale} fill={this.props.mark.color} x={x1 + width / 2} y={y1 + height * (y1 < 50 ? 6 : -2)} label={this.props.mark.label} />
            </g>
          </Draggable>

          {this.props.selected &&
            (deleteButtonPos = this.getDeleteButtonPosition()) &&
            <DeleteButton onClick={this.props.onDestroy} scale={scale} x={deleteButtonPos.x} y={deleteButtonPos.y} />
          }

          { // REQUIRES MARK-BUTTON-MIXIN
            (this.props.selected || this.state.markStatus == 'transcribe-enabled') &&
            this.props.isTranscribable && this.renderMarkButton()
          }

        </g>
      </g>
    )
  }
}
