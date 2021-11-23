/*
 * decaffeinate suggestions:
 * DS101: Remove unnecessary use of Array.from
 * DS102: Remove unnecessary code created because of implicit returns
 * DS103: Rewrite code to no longer use __guard__
 * DS104: Avoid inline assignments
 * DS205: Consider reworking code to avoid use of IIFEs
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React from 'react'
import createReactClass from 'create-react-class'
import { NavLink } from 'react-router-dom'
import { AppContext } from '../app-context.jsx'
import SubjectSetViewer from '../subject-set-viewer.jsx'
import FetchSubjectSetsMixin from '../../lib/fetch-subject-sets-mixin.jsx'
import BaseWorkflowMethods from '../../lib/workflow-methods-mixin.jsx'
import ForumSubjectWidget from '../forum-subject-widget.jsx'
import HelpModal from '../help-modal.jsx'
import Tutorial from '../tutorial.jsx'
import HelpButton from '../buttons/help-button.jsx'
import BadSubjectButton from '../buttons/bad-subject-button.jsx'
import DraggableModal from '../draggable-modal.jsx'
import queryString from 'query-string'
import SubjectSetSelector from '../subject-set-selector.jsx'
import NoMoreSubjectsModal from '../no-more-subjects-modal'

export default AppContext(createReactClass({
  // rename to Classifier
  displayName: 'Mark',

  getDefaultProps() {
    return { workflowName: 'mark' }
  },
  // hideOtherMarks: false

  mixins: [FetchSubjectSetsMixin, BaseWorkflowMethods], // load subjects and set state variables: subjects, currentSubject, classification

  getInitialState() {
    return {
      badSubject: false,
      nothingToMark: false,
      taskKey: null,
      classifications: [],
      classificationIndex: 0,
      subject_set_index: 0,
      subject_index: 0,
      currentSubToolIndex: 0,
      helping: false,
      hideOtherMarks: false,
      currentSubtool: null,
      showingTutorial: this.showTutorialBasedOnUser(this.props.context.user),
      lightboxHelp: false,
      activeSubjectHelper: null,
      subjectCurrentPage: 1,
      selectSubjectSet: true,
    }
  },

  componentWillReceiveProps(new_props) {
    this.setState({
      showingTutorial: this.showTutorialBasedOnUser(new_props.context.user)
    })
  },

  showTutorialBasedOnUser(user) {
    // Show tutorial by default
    let show = true
    if ((user != null ? user.tutorial_complete : undefined) != null) {
      // If we have a user, show tutorial if they haven't completed it:
      show = !user.tutorial_complete
    }
    return show
  },

  componentDidMount() {
    this.getCompletionAssessmentTask()
    this.fetchSubjectSetsBasedOnProps()
    this.fetchGroups()
  },

  componentWillMount() {
    this.setState({ taskKey: this.getActiveWorkflow().first_task })
    this.beginClassification()
  },



  componentDidUpdate(prev_props) {
    // If visitor nav'd from, for example, /mark/[some id] to /mark, this component won't re-mount, so detect transition here:
    if (prev_props.hash !== this.props.hash) {
      this.fetchSubjectSetsBasedOnProps()
    }
  },

  toggleHelp() {
    this.setState({ helping: !this.state.helping })
    return this.hideSubjectHelp()
  },

  toggleTutorial() {
    this.setState({ showingTutorial: !this.state.showingTutorial })
    return this.hideSubjectHelp()
  },

  toggleLightboxHelp() {
    this.setState({ lightboxHelp: !this.state.lightboxHelp })
    return this.hideSubjectHelp()
  },

  toggleHideOtherMarks() {
    return this.setState({ hideOtherMarks: !this.state.hideOtherMarks })
  },

  // User changed currently-viewed subject:
  handleViewSubject(index) {
    this.setState({ subject_index: index }, () => this.forceUpdate())
    if (this.state.badSubject) {
      return this.toggleBadSubject()
    }
    if (this.state.nothingToMark) {
      return this.toggleNothingToMark()
    }
  },

  isLastSubjectInSubjectSet() {
    return this.getCurrentSubject() === this.getCurrentSubjectSet().subjects[this.getCurrentSubjectSet().subjects.length - 1]
  },

  navigateTaskOrNextPage() {
    // Alex Hebing: if this our new task, and the answer is no, complete subject and navigate to next page
    if (this.state.taskKey === 'anything_left_to_mark' &&
      this.state.classifications[this.state.classificationIndex].annotation.value.toLowerCase() == 'no') {
      this.completeSubjectSet()
      this.completeSubjectAssessment()
    } else {
      this.advanceToNextTask()
    }
  },

  getNavigationalButton(waitingForAnswer) {
    if (this.hasPickOneButtonsTool() && !this.state.badSubject) {
      return (undefined)
    }

    if (this.state.taskKey === 'completion_assessment_task') {
      return (
        <button
          type="button"
          className="continue major-button"
          disabled={waitingForAnswer}
          onClick={this.completeSubjectAssessment}
        >
          Next
        </button>
      )
    } else if (!this.state.nothingToMark && !this.state.badSubject) {
      return (
        <button
          type="button"
          className="continue major-button"
          disabled={waitingForAnswer}
          onClick={this.getNextTask() ? this.navigateTaskOrNextPage : this.completeSubjectSet}
        >
          {this.state.taskKey === 'anything_left_to_mark' &&
            `${this.state.classifications[this.state.classificationIndex].annotation.value}`.toLowerCase() == 'no' ?
            'Done' :
            'Next'}
        </button>
      )
    } else if (this.state.badSubject || this.state.nothingToMark) {
      return (
        <button
          type="button"
          className="continue major-button"
          onClick={this.completeSubjectSet}
        >
          Done
        </button>
      )
    } else {
      return (undefined)
    }
  },

  hasPickOneButtonsTool() {
    const task = this.getCurrentTask()
    return task.tool == 'pickOneButtons'
  },

  // User somehow indicated current task is complete; commit current classification
  handleToolComplete(annotation) {
    this.handleDataFromTool(annotation)
    return this.createAndCommitClassification(annotation)
  },

  // Handle user selecting a pick/drawing tool:
  handleDataFromTool(d) {
    // Kind of a hack: We receive annotation data from two places:
    //  1. tool selection widget in right-col
    //  2. the actual draggable marking tools
    // We want to remember the subToolIndex so that the right-col menu highlights
    // the correct tool after committing a mark. If incoming data has subToolIndex
    // but no mark location information, we know this callback was called by the
    // right-col. So only in that case, record currentSubToolIndex, which we use
    // to initialize marks going forward
    if (d.subToolIndex != null && d.x == null && d.y == null) {
      this.setState({ currentSubToolIndex: d.subToolIndex })
      if (d.tool != null) {
        return this.setState({ currentSubtool: d.tool })
      }
    } else {
      const { classifications } = this.state
      for (let k in d) {
        const v = d[k]
        classifications[this.state.classificationIndex].annotation[k] = v
      }
      // PB: Saving STI's notes here in case we decide tools should fully
      //   replace annotation hash rather than selectively update by key as above:
      // not clear whether we should replace annotations, or append to it --STI
      // classifications[@state.classificationIndex].annotation = d #[k] = v for k, v of d

      return this.setState({ classifications }, () => {
        if (this.state.taskKey === 'completion_assessment_task') { // equivalent of Next (Page) button
          this.completeSubjectAssessment()
        } else if (this.hasPickOneButtonsTool()) {
          // PickOneButtons get navigated on clicking on the answer
          if (this.getNextTask()) {
            this.advanceToNextTask()
          } else {
            // ask for the completion assessment
            this.completeSubjectSet()
          }
        }

        return this.forceUpdate()
      })
    }
  },

  handleMarkDelete(m) {
    this.flagSubjectAsUserDeleted(m.subject_id)
  },

  destroyCurrentClassification() {
    const { classifications } = this.state
    classifications.splice(this.state.classificationIndex, 1)
    this.setState({
      classifications,
      classificationIndex: classifications.length - 1
    })

    // There should always be an empty classification ready to receive data:
    return this.beginClassification()
  },

  destroyCurrentAnnotation() { },
  // TODO: implement mechanism for going backwards to previous classification, potentially deleting later classifications from stack:
  // @props.classification.annotations.pop()

  onSubjectSetSelected(subjectSetId) {
    this.setState({ selectSubjectSet: false })
    this.props.match.params.subject_set_id = subjectSetId
    this.fetchSubjectSetsBasedOnProps()
  },

  completeSubjectSet() {
    this.commitCurrentClassification()
    this.beginClassification()

    // TODO: Should maybe make this workflow-configurable?
    const showSubjectAssessment = !this.state.badSubject
    if (showSubjectAssessment) {
      return this.setState({
        taskKey: 'completion_assessment_task'
      })
    } else {
      return this.advanceToNextSubject()
    }
  },

  completeSubjectAssessment() {
    this.commitCurrentClassification()
    this.beginClassification()
    return this.advanceToNextSubject()
  },

  nextPage(callback_fn) {
    return this.jumpPage(this.state.subjectCurrentPage + 1, callback_fn)
  },

  prevPage(callback_fn) {
    return this.jumpPage(this.state.subjectCurrentPage - 1, callback_fn)
  },

  jumpPage(newPage, callback_fn) {
    this.setState({ subjectCurrentPage: newPage })
    return this.fetchSubjectsForCurrentSubjectSet(newPage, null, callback_fn)
  },

  showSubjectHelp(subject_type) {
    return this.setState({
      activeSubjectHelper: subject_type,
      helping: false,
      showingTutorial: false,
      lightboxHelp: false
    })
  },

  hideSubjectHelp() {
    return this.setState({
      activeSubjectHelper: null
    })
  },

  render() {
    let left1, waitingForAnswer
    let tool
    if (this.getCurrentSubjectSet() == null || this.getActiveWorkflow() == null) {
      return null
    }

    const currentTask = this.getCurrentTask()
    const TaskComponent = this.getCurrentTool()
    const activeWorkflow = this.getActiveWorkflow()
    const firstTask = activeWorkflow.first_task
    const onFirstAnnotation = this.state.taskKey === firstTask
    const currentSubtool = this.state.currentSubtool
      ? this.state.currentSubtool
      : __guard__(
        __guard__(this.getTasks()[firstTask], x1 => x1.tool_config.tools),
        x => x[0]
      )

    // direct link to this page
    const pageURL = `${location.origin}/#/mark?subject_set_id=${
      this.getCurrentSubjectSet().id
      }&selected_subject_id=${__guard__(this.getCurrentSubject(), x2 => x2.id)}`

    if ((currentTask != null ? currentTask.tool : undefined) === 'pickOne') {
      const currentAnswer = Array.from(currentTask.tool_config.options).filter(
        a => a.value === this.getCurrentClassification().annotation.value
      )[0]

      waitingForAnswer = !currentAnswer
    }

    return (
      <div className="classifier mark">
        <div className="subject-area">
          {(() => {
            if (this.state.noMoreSubjects || this.state.noMoreSubjectSets) {
              return (
                <NoMoreSubjectsModal header="Nothing more to mark" workflowName={this.props.workflowName} project={this.props.context.project} />
              )
            } else if (this.state.notice) {
              return (
                <DraggableModal
                  header={this.state.notice.header}
                  onDone={this.state.notice.onClick}
                >
                  {this.state.notice.message}
                </DraggableModal>
              )
            } else if (this.state.selectSubjectSet) {
              let query = queryString.parse(this.props.location.search)

              return (
                <SubjectSetSelector
                  subjectSets={this.state.subjectSets}
                  onSelected={this.onSubjectSetSelected}
                  group_id={query.group_id}
                >
                </SubjectSetSelector>
              )
            } else if (this.getCurrentSubjectSet() != null) {
              let left
              return (
                <SubjectSetViewer
                  subject_set={this.getCurrentSubjectSet()}
                  subject_index={this.state.subject_index}
                  workflow={this.getActiveWorkflow()}
                  task={currentTask}
                  annotation={
                    (left = __guard__(
                      this.getCurrentClassification(),
                      x3 => x3.annotation
                    )) != null
                      ? left
                      : {}
                  }
                  onComplete={this.handleToolComplete}
                  onChange={this.handleDataFromTool}
                  onDestroy={this.handleMarkDelete}
                  onViewSubject={this.handleViewSubject}
                  subToolIndex={this.state.currentSubToolIndex}
                  nextPage={this.nextPage}
                  prevPage={this.prevPage}
                  jumpPage={this.jumpPage}
                  subjectCurrentPage={this.state.subjectCurrentPage}
                  totalSubjectPages={this.state.subjects_total_pages}
                  destroyCurrentClassification={
                    this.destroyCurrentClassification
                  }
                  hideOtherMarks={this.state.hideOtherMarks}
                  toggleHideOtherMarks={this.toggleHideOtherMarks}
                  currentSubtool={currentSubtool}
                  lightboxHelp={this.toggleLightboxHelp}
                  interimMarks={this.state.interimMarks}
                />
              )
            }
          })()}
        </div>
        {!this.state.selectSubjectSet &&
          <div className="right-column">
            <div className={`task-area ${this.getActiveWorkflow().name}`}>
              {this.getCurrentTask() != null &&
                this.getCurrentSubject() != null ? (
                  <div className="task-container">
                    <TaskComponent
                      key={this.getCurrentTask().key}
                      task={currentTask}
                      disabled={this.state.badSubject}
                      annotation={
                        (left1 = __guard__(
                          this.getCurrentClassification(),
                          x4 => x4.annotation
                        )) != null
                          ? left1
                          : {}
                      }
                      onChange={this.handleDataFromTool}
                      onSubjectHelp={this.showSubjectHelp}
                      subject={this.getCurrentSubject()}
                    />
                    <nav className="task-nav">
                      {false &&
                        <button
                          type="button"
                          className="back minor-button"
                          disabled={onFirstAnnotation}
                          onClick={this.destroyCurrentAnnotation}
                        >
                          Back
                        </button>}
                      {this.getNavigationalButton(waitingForAnswer)}
                    </nav>
                    <div className="help-bad-subject-holder">
                      {this.getCurrentTask().help != null &&
                        <HelpButton
                          onClick={this.toggleHelp}
                          label=""
                          className="task-help-button"
                        />}
                      {onFirstAnnotation && !this.state.nothingToMark &&
                        <BadSubjectButton
                          class="bad-subject-button"
                          label={`Bad ${this.props.context.project.term('subject')}`}
                          active={this.state.badSubject}
                          onClick={this.toggleBadSubject}
                        />
                      }
                      {this.state.badSubject &&
                        <p className="bad-subject-marked">
                          <span>
                            You&#39;ve marked this {this.props.context.project.term('subject')} as
                      BAD. Thanks for flagging the issue!{' '}</span>
                          <strong>Press DONE to continue.</strong>
                        </p>}
                      {onFirstAnnotation && this.props.context.project.show_nothing_to_mark_button && !this.state.badSubject &&
                        <BadSubjectButton
                          class="bad-subject-button"
                          label="Nothing to mark"
                          active={this.state.nothingToMark}
                          onClick={this.toggleNothingToMark}
                        />
                      }
                      {this.state.nothingToMark &&
                        <p className="bad-subject-marked">
                          <span>
                            You&#39;ve marked this {this.props.context.project.term('subject')} as
                      having nothing to mark. Thanks for flagging the issue!{' '}</span>
                          <strong>Press DONE to continue.</strong>
                        </p>}
                    </div>
                  </div>
                ) : (
                  undefined
                )}
              {
                this.props.context.project.contact_details === '' || this.props.context.project.contact_details == null ? undefined : (
                  <p className='contact-details'>{this.props.context.project.contact_details}</p>)
              }
              <div className="task-secondary-area">

                {this.getCurrentTask() != null &&
                  <p>
                    <a className="tutorial-link" onClick={this.toggleTutorial}>
                      View A Tutorial
                    </a>
                  </p>}
                {
                  this.getActiveWorkflow().show_transcribe_now_button &&
                  this.getCurrentTask() != null &&
                  this.getActiveWorkflow() != null &&
                  this.getWorkflowByName('transcribe') != null &&
                  <p>
                    <NavLink
                      to={`/transcribe/${this.getWorkflowByName('transcribe').id}/${
                        __guard__(this.getCurrentSubject(), x5 => x5.id)}`}
                      className="transcribe-link">
                      Transcribe this {this.props.context.project.term('subject')} now!
                    </NavLink>
                  </p>}
                {this.getActiveWorkflow() != null &&
                  (this.state.groups != null
                    ? this.state.groups.length
                    : undefined) > 1 ? (
                    <p>
                      <NavLink
                        to={`/groups/${this.getCurrentSubjectSet().group_id}`}
                        className="about-link"
                        target="_blank"
                      >
                        About this {this.props.context.project.term('group')}.
                      </NavLink>
                    </p>
                  ) : (
                    undefined
                  )}
                <div className="forum-holder">
                  <ForumSubjectWidget
                    subject={this.getCurrentSubject()}
                    subject_set={this.getCurrentSubjectSet()}
                    project={this.props.context.project}
                  />
                </div>
                <div className="social-media-container">
                  <a
                    href={`https://www.facebook.com/sharer.php?u=${encodeURIComponent(
                      pageURL
                    )}`}
                    target="_blank"
                  >
                    <i className="fa fa-facebook-square" />
                  </a>
                  <a
                    href={`https://twitter.com/home?status=${encodeURIComponent(
                      pageURL
                    )}%0A`}
                    target="_blank"
                  >
                    <i className="fa fa-twitter-square" />
                  </a>
                </div>
              </div>
            </div>
          </div>}
        {this.props.context.project.tutorial != null && this.state.showingTutorial && !this.state.selectSubjectSet && (
          // Check for workflow-specific tutorial
          this.props.context.project.tutorial.workflows != null &&
            this.props.context.project.tutorial.workflows[
            __guard__(this.getActiveWorkflow(), x6 => x6.name)
            ] ? (
              <Tutorial
                tutorial={
                  this.props.context.project.tutorial.workflows[
                  this.getActiveWorkflow().name
                  ]
                }
                onCloseTutorial={this.props.context.onCloseTutorial}
              />
            ) : (
              // Otherwise just show general tutorial
              <Tutorial
                tutorial={this.props.context.project.tutorial}
                onCloseTutorial={this.props.context.onCloseTutorial}
              />
            )
        )}
        {this.state.helping &&
          <HelpModal
            help={this.getCurrentTask().help}
            onDone={() => this.setState({ helping: false })}
          />}
        {this.state.lightboxHelp &&
          <HelpModal
            help={{
              title: 'The Lightbox',
              body:
                '<p>This Lightbox displays a complete set of documents in order. You can use it to go through the documents sequentially—but feel free to do them in any order that you like! Just click any thumbnail to open that document and begin marking it.</p><p>However, please note that **once you start marking a page, the Lightbox becomes locked ** until you finish marking that page! You can select a new page once you have finished.</p>'
            }}
            onDone={() => this.setState({ lightboxHelp: false })}
          />}
        {this.getCurrentTask() != null && (() => {
          const result = []
          const iterable = this.getCurrentTask().tool_config.options
          for (let i = 0; i < iterable.length; i++) {
            tool = iterable[i]
            if (
              tool.help &&
              tool.generates_subject_type &&
              this.state.activeSubjectHelper === tool.generates_subject_type
            ) {
              result.push(
                <HelpModal help={tool.help} onDone={this.hideSubjectHelp} />
              )
            } else {
              result.push(undefined)
            }
          }
          return result
        })()}
      </div>
    )
  }
}))

window.React = React

function __guard__(value, transform) {
  return typeof value !== 'undefined' && value !== null
    ? transform(value)
    : undefined
}
