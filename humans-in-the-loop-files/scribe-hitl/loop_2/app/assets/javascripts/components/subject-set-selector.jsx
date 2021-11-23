/*
 * Author: Alex Hebing @ Digital Humanities Lab (Utrecht University), 2019
 */
import React from 'react'
import PropTypes from 'prop-types'
import API from '../lib/api.jsx'
import { AppContext } from './app-context.jsx'
import DraggableModal from './draggable-modal'
import GenericButton from './buttons/generic-button'

@AppContext
export default class SubjectSetSelector extends React.Component {
  static defaultProps = {
    classes: '',
    doneButtonLabel: 'Give me a random source'
  }

  static contextTypes = {
    router: PropTypes.object
  }

  constructor() {
    super()
    this.state = {
      redirect: false,
      subjectSetId: null
    }
  }

  componentDidMount() {
    const project_id = this.props.context.project.id
    API.type('groups')
      .get({ project_id })
      .then(groupList => {
        const groups = {}
        for (let group of groupList) {
          groups[group.id] = group
        }
        this.setState({ groups })
      })
  }

  componentWillMount() {
    const subjectSets = this.props.subjectSets
    if (subjectSets.length === 1) {
      this.onSubjectSetSelected(subjectSets[0].id)
    }
  }

  sortByGroupId(subjectSets) {
    subjectSets.sort(function (a, b) {
      if (a.group_id < b.group_id) { return -1 }
      if (a.group_id > b.group_id) { return 1 }
      return 0
    })
  }

  getSubjectSets(subjectSets) {
    let subjectSetTitles = []
    let currentGroupName
    let currentGroupItems

    if (subjectSets.length > 1) {
      this.sortByGroupId(subjectSets)
    }

    const sorted = subjectSets
      .map(subjectSet => ({
        id: subjectSet.id,
        groupName: this.state.groups[subjectSet.group_id].name,
        hide: subjectSet.meta_data.hide || false,
        label: parseTitle(subjectSet.meta_data.set_key)
      }))
      .filter(s => !s.hide)
      .sort((a, b) => {
        // sort by groupName then by label (title)
        if (a.groupName > b.groupName) {
          return 1
        } else if (a.groupName < b.groupName) {
          return -1
        }
        return a.label >= b.label ? 1 : -1
      })

    for (var i = 0; i < sorted.length; i++) {
      let { id, groupName, label } = sorted[i]

      // if Mark is navigated to via menu (not a specific groupName)...
      if (!this.props.group_id) {
        // ... add groupName headers 
        if (i === 0 || currentGroupName !== groupName) {
          currentGroupItems = []
          subjectSetTitles.push(<fieldset key={i}>
            <legend>{groupName}</legend>
            {currentGroupItems}
          </fieldset>)
          currentGroupName = groupName
        }
      } else {
        currentGroupItems = subjectSetTitles
      }

      currentGroupItems.push(
        <GenericButton
          key={id}
          label={label}
          className="ghost small-button selectable-subject-set"
          onClick={() => {
            this.onSubjectSetSelected(id)
          }}>
        </GenericButton>)
    }
    return <div>{subjectSetTitles}</div>
  }

  onSelectRandomSubjectSet = () => {
    this.onSubjectSetSelected(undefined)
  }

  onSubjectSetSelected = (subjectSetId) => {
    let { onSelected } = this.props
    onSelected(subjectSetId)
  }

  render() {
    const subjectSets = this.props.subjectSets
    return (
      <DraggableModal
        ref="tutorialModal"
        header='Please select a source'
        doneButtonLabel="Give me a random source"
        onDone={this.onSelectRandomSubjectSet}
        width={800}
        classes="help-modal subject-set-selector"
        closeButton={true}
        onClose={this.onSelectRandomSubjectSet}>
        {!this.state.groups && <div className="is-loading" style={{ height: '100px' }}></div>}
        {this.state.groups && <div>
          <p>Please select the source you would like to work on.</p>
          {this.getSubjectSets(subjectSets)}
        </div>}
      </DraggableModal>
    )
  }
}

export function parseTitle(subjectSetKey) {
  // skip the page numbers
  let yearIndex = subjectSetKey.search(/\d{4}.*$/)
  if (yearIndex > 10) {
    subjectSetKey = `${subjectSetKey.substring(0, yearIndex).replace(/-+$/g, '')}, ${parseYearParts(subjectSetKey.substr(yearIndex))}`
  }
  return subjectSetKey.replace(/-/g, ' ')
}

function parseYearParts(yearParts) {
  const yearSearch = /\d{4}/g
  let min = 0, max = 0
  let match
  while ((match = yearSearch.exec(yearParts))) {
    let year = parseInt(match, 10)
    if (min == 0) {
      min = year
    }
    if (year > max) {
      max = year
    }
  }

  return max > min ? `${min} — ${max}` : min
}