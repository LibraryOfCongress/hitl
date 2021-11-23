import React from 'react'
import PropTypes from 'prop-types'
import SVGImage from './svg-image.jsx'
import ActionButton from './action-button.jsx'

/**
 * Number of subjects in a subject set page.
 */
const PageSize = 120
const ThumbSize = 3

export default class LightBox extends React.Component {
  static propTypes = {
    subject_set: PropTypes.object.isRequired,
    subject_index: PropTypes.number.isRequired,
    onSubject: PropTypes.func.isRequired,
    nextPage: PropTypes.func.isRequired,
    prevPage: PropTypes.func.isRequired,
    jumpPage: PropTypes.func.isRequired,
    totalSubjectPages: PropTypes.number,
    subjectCurrentPage: PropTypes.number
  }

  constructor(props) {
    super(props)
    this.state = {
      first: props.subject_set.subjects[0],
      manualPageOrder: props.subject_set.subjects[0].order,
      folded: false
    }
  }

  handleFoldClick = () => {
    this.setState({ folded: !this.state.folded })
  }

  lightBoxMessage = () => {
    if (this.state.folded) {
      return 'Show Lightbox'
    } else {
      return 'Hide Lightbox'
    }
  }

  render() {
    // window.subjects = @props.subject_set.subjects # pb ?
    let carouselStyle
    if (this.props.subject_set.subjects.length <= 1) {
      return null
    }
    const indexOfFirst = this.findSubjectIndex(this.state.first)
    const second = this.props.subject_set.subjects[indexOfFirst + 1]
    const third = this.props.subject_set.subjects[indexOfFirst + 2]

    const viewBox = [0, 0, 100, 100]

    if (this.state.folded) {
      carouselStyle = {
        display: 'none'
      }
    }

    const classes = []
    if (this.props.isDisabled) {
      classes.push('disabled')
    }

    const containerClasses = []
    containerClasses.push('light-box-area')
    if (this.state.folded) {
      containerClasses.push('folded')
    }

    return (
      <div className={containerClasses.join(' ')}>
        <div className="carousel">
          <div id="visibility-button">
            <svg
              onClick={this.props.toggleLightboxHelp}
              id="questions-tip"
              width="14px"
              height="14px"
              viewBox="0 0 14 14"
            >
              <path fillRule="evenodd" d="M 7 0C 3.13 0-0 3.13-0 7-0 10.87 3.13 14 7 14 10.87 14 14 10.87 14 7 14 3.13 10.87 0 7 0ZM 7.04 11.13C 6.51 11.13 6.07 10.68 6.07 10.15 6.07 9.63 6.51 9.18 7.04 9.18 7.57 9.18 8.01 9.63 8.01 10.15 8.01 10.68 7.57 11.13 7.04 11.13ZM 7.56 7.66C 7.56 7.85 7.65 8.06 7.77 8.16 7.77 8.16 6.47 8.55 6.47 8.55 6.21 8.27 6.07 7.91 6.07 7.49 6.07 6.06 7.82 5.9 7.82 5.07 7.82 4.7 7.54 4.39 6.89 4.39 6.29 4.39 5.78 4.69 5.41 5.13 5.41 5.13 4.44 4.04 4.44 4.04 5.07 3.29 6.03 2.87 7.07 2.87 8.61 2.87 9.56 3.65 9.56 4.77 9.56 6.52 7.56 6.65 7.56 7.66Z" fill="rgb(187,191,195)" />
            </svg>
          </div>
          <div id="image-list" className={classes} style={carouselStyle}>
            <ul>
              <li
                onClick={this.shineSelected.bind(
                  this,
                  this.findSubjectIndex(this.state.first)
                )}
                className={
                  this.props.subject_index ===
                    this.findSubjectIndex(this.state.first)
                    ? 'active'
                    : undefined
                }
              >
                <span className="page-number">{this.state.first.order}</span>
                <svg
                  className="light-box-subject"
                  width={125}
                  height={125}
                  viewBox={viewBox}
                >
                  <SVGImage
                    src={
                      this.state.first.location.thumbnail != null
                        ? this.state.first.location.thumbnail
                        : this.state.first.location.standard
                    }
                    width={100}
                    height={100}
                  />
                </svg>
              </li>
              {second &&
                <li
                  onClick={this.shineSelected.bind(
                    this,
                    this.findSubjectIndex(second)
                  )}
                  className={
                    this.props.subject_index === this.findSubjectIndex(second)
                      ? 'active'
                      : undefined
                  }
                >
                  <span className="page-number">{second.order}</span>
                  <svg
                    className="light-box-subject"
                    width={125}
                    height={125}
                    viewBox={viewBox}
                  >
                    <SVGImage
                      src={
                        second.location.thumbnail != null
                          ? second.location.thumbnail
                          : second.location.standard
                      }
                      width={100}
                      height={100}
                    />
                  </svg>
                </li>
              }
              {third &&
                <li
                  onClick={this.shineSelected.bind(
                    this,
                    this.findSubjectIndex(third)
                  )}
                  className={
                    this.props.subject_index === this.findSubjectIndex(third)
                      ? 'active'
                      : undefined
                  }
                >
                  <span className="page-number">{third.order}</span>
                  <svg
                    className="light-box-subject"
                    width={125}
                    height={125}
                    viewBox={viewBox}
                  >
                    <SVGImage
                      src={
                        third.location.thumbnail != null
                          ? third.location.thumbnail
                          : third.location.standard
                      }
                      width={100}
                      height={100}
                    />
                  </svg>
                </li>
              }
            </ul>
            <input type="number" className="page-field" value={this.state.manualPageOrder} onChange={this.moveIndex} />
            <ActionButton
              type="back"
              text="BACK"
              onClick={this.moveBack.bind(this, indexOfFirst)}
              classes={this.backButtonDisable(indexOfFirst)}
            />
            <ActionButton
              type="next"
              text="NEXT"
              onClick={this.moveForward.bind(this, indexOfFirst, third, second)}
              classes={this.forwardButtonDisable(
                third != null ? third : undefined
              )}
            />
          </div>
        </div>
      </div>
    )
  }

  // allows user to click on a subject in the lightbox to load that subject into the subject-viewer.
  // This method ultimately sets the state.subject_index in mark/index. See subject-set-viewer#specificSelection() and mark/index#handleViewSubject().
  shineSelected(index) {
    this.props.onSubject(index)
  }

  // determines the back button css
  backButtonDisable = (indexOfFirst) => {
    if (
      this.props.subjectCurrentPage === 1 &&
      this.props.subject_set.subjects[indexOfFirst] ===
      this.props.subject_set.subjects[0]
    ) {
      return 'disabled'
    } else {
      return ''
    }
  }

  // determines the forward button css
  forwardButtonDisable(third) {
    if (
      this.props.subjectCurrentPage === this.props.totalSubjectPages &&
      (this.props.subject_set.subjects.length <= 3 ||
        third ===
        this.props.subject_set.subjects[this.props.subject_set.subjects.length - 1])
    ) {
      return 'disabled'
    } else {
      return ''
    }
  }

  // finds the index of a given subject within the current page of the subject_set
  findSubjectIndex(subject_arg) {
    // PB sometimes equality is failing on subjects, so let's try just matching id
    // return @props.subject_set.subjects.indexOf subject_arg
    return this.props.subject_set.subjects.findIndex(s => s.id == subject_arg.id)
  }

  moveIndex = (e) => {
    const manualPageOrder = parseInt(e.target.value)
    this.setState({ manualPageOrder })
    if (!isNaN(manualPageOrder)) {
      const desiredPage = Math.floor(manualPageOrder / PageSize) + 1
      if (this.props.subjectCurrentPage == desiredPage) {
        this.moveIndexIteration(manualPageOrder)
      } else {
        this.props.jumpPage(desiredPage, () => {
          this.moveIndexIteration(manualPageOrder)
        })
      }
    }
  }

  moveIndexIteration(manualPageOrder) {
    const subjects = this.props.subject_set.subjects
    const index = subjects.findIndex(s => s.order == manualPageOrder)

    if (index != -1) {
      const first = subjects[Math.floor(index / ThumbSize) * ThumbSize]
      this.setState({ first })
      this.shineSelected(index)
    }
  }

  // allows user to navigate back though a subject_set
  // # controls navigation of current page of subjects as well as the method that pull a new page of subjects
  moveBack(indexOfFirst, callback = null) {
    // if the current page of subjects is the first page of subjects, and the first <li> is the first subject in the page of subjects.
    if (
      this.props.subjectCurrentPage === 1 &&
      this.props.subject_set.subjects[indexOfFirst] ===
      this.props.subject_set.subjects[0]
    ) {
      if (callback) callback()
    } else if (
      this.props.subjectCurrentPage > 1 &&
      this.props.subject_set.subjects[indexOfFirst] ===
      this.props.subject_set.subjects[0]
    ) {
      this.props.prevPage()
    } else {
      this.setState({
        first: this.props.subject_set.subjects[indexOfFirst - 3]
      }, callback)
    }
  }

  moveForward(indexOfFirst, third, second, callback = null) {
    // if the current page of subjects is the last page of the subject_set and the 2nd or 3rd <li> is the last <li> contain the last subjects in the subject_set
    if (
      this.props.subjectCurrentPage === this.props.totalSubjectPages &&
      (third ===
        this.props.subject_set.subjects[this.props.subject_set.subjects.length - 1] ||
        second ===
        this.props.subject_set.subjects[this.props.subject_set.subjects.length - 1])
    ) {
      if (callback) { callback() }
      return
    }
    // # if the current page of subjects is NOT the last page of the subject_set and the 2nd or 3rd <li> is the last <li> contain the last subjects in the subject_set
    if (
      this.props.subjectCurrentPage < this.props.totalSubjectPages &&
      (third ===
        this.props.subject_set.subjects[this.props.subject_set.subjects.length - 1] ||
        second ===
        this.props.subject_set.subjects[this.props.subject_set.subjects.length - 1])
    ) {
      this.props.nextPage()
      // NOTE: for some reason, LightBox does not receive correct value for @props.subject_index, which has led to this awkard callback function above --STI
      // @setState first: @props.subject_set.subjects[0], => @forceUpdate()

      // there are further subjects to see in the currently loaded page
    } else {
      this.setState({
        first: this.props.subject_set.subjects[indexOfFirst + 3]
      }, callback)
    }
  }
}
