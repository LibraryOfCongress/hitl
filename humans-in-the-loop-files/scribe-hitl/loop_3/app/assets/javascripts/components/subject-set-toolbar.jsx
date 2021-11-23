import React from 'react'
import PropTypes from 'prop-types'
import LightBox from './light-box.jsx'
import SubjectZoomPan from './subject-zoom-pan.jsx'

export default class SubjectSetToolbar extends React.Component {
  displayName = 'SubjectSetToolbar'

  static propTypes = {
    hideOtherMarks: PropTypes.bool.isRequired,
    lightboxHelp: PropTypes.func,
    nextPage: PropTypes.func.isRequired,
    onExpand: PropTypes.func,
    onHide: PropTypes.func,
    onSubject: PropTypes.func.isRequired,
    onZoomChange: PropTypes.func,
    prevPage: PropTypes.func.isRequired,
    subject: PropTypes.object,
    subjectCurrentPage: PropTypes.number,
    subject_index: PropTypes.number.isRequired,
    subject_set: PropTypes.object.isRequired,
    task: PropTypes.object,
    toggleHideOtherMarks: PropTypes.func,
    totalSubjectPages: PropTypes.number,
    viewBox: PropTypes.arrayOf(PropTypes.number),
    workflow: PropTypes.object
  }

  constructor(props) {
    super(props)
    this.state = {
      subject_set: this.props.subject_set,
      zoomPanViewBox: this.props.viewBox,
      activePane: '',
      hideMarks: true
    }
    this.hidePane = this.hidePane.bind(this)
  }

  componentWillUnmount() {
    if (this.state.activePane) {
      document.removeEventListener('mousedown', this.hidePane)
    }
  }

  togglePane(name) {
    this.setState((prevState) => {
      if (prevState.activePane) {
        if (prevState.activePane === name || name === '') {
          // close it
          document.removeEventListener('mousedown', this.hidePane)
          this.props.onHide()
          return { activePane: '' }
        }
      } else if (name !== '') {
        // open a new pane
        document.addEventListener('mousedown', this.hidePane)
        this.props.onExpand()
      }

      return { activePane: name }
    })
  }

  setToolbarRef(node) {
    this.wrapperRef = node
  }

  hidePane(event) {
    if (this.wrapperRef && !this.wrapperRef.contains(event.target)) {
      this.togglePane('')
    }
  }

  render() {
    // disable LightBox if work has begun
    const disableLightBox = this.props.task.key !== this.props.workflow.first_task
    return (
      <div ref={this.setToolbarRef.bind(this)} className="subject-set-toolbar">
        <div className="subject-set-toolbar-panes">
          <div
            className={`light-box-area multi-page pane${this.state.activePane === 'multi-page' ? ' active' : ''}`}
          >
            {this.props.subject_set && this.props.subject_set.subjects.length ? (
              <LightBox
                subject_set={this.props.subject_set}
                subject_index={this.props.subject_index}
                key={this.props.subject_set.subjects[0].id}
                isDisabled={disableLightBox}
                toggleLightboxHelp={this.props.lightboxHelp}
                onSubject={this.props.onSubject}
                subjectCurrentPage={this.props.subjectCurrentPage}
                nextPage={this.props.nextPage}
                prevPage={this.props.prevPage}
                jumpPage={this.props.jumpPage}
                totalSubjectPages={this.props.totalSubjectPages}
              />
            ) : undefined}
          </div>
          <div
            className={`pan-zoom-area pan-zoom pane ${this.state.activePane === 'pan-zoom' ? ' active' : ''}`}
          >
            <SubjectZoomPan subject={this.props.subject} onChange={this.props.onZoomChange} viewBox={this.state.zoomPanViewBox} />
          </div>


        </div>
        <div className="subject-set-toolbar-links">
          <a className={`toggle-pan-zoom${this.state.activePane === 'pan-zoom' ? ' active' : ''}`}
            onClick={this.togglePane.bind(this, 'pan-zoom')}>
            <div className="helper">Toggle pan and zoom tool</div>
          </a>
          <a className={`toggle-multi-page${this.props.subject_set.subjects.length <= 1 ? ' disabled' : ''}${this.state.activePane === 'multi-page' ? ' active' : ''}`}
            onClick={this.togglePane.bind(this, 'multi-page')}>
            <div className="helper">Toggle multi-page navigation</div>
          </a>
          <a className={this.props.hideOtherMarks === true
            ? 'fa fa-toggle-on fa-2x'
            : 'fa fa-toggle-off fa-2x'
          } onClick={this.props.toggleHideOtherMarks}>
            <div className="helper">
              {this.props.hideOtherMarks === false
                ? 'Hide Marks of Other People'
                : 'Showing Only Your Marks'}
            </div>
          </a>
        </div>
      </div>
    )
  }
}
