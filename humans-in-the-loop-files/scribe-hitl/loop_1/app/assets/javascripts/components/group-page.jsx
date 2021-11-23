import React from 'react'
import pluralize from 'pluralize'

import GenericButton from './buttons/generic-button.jsx'
import API from '../lib/api.jsx'
import { AppContext } from './app-context.jsx'

@AppContext
export default class GroupPage extends React.Component {
  constructor() {
    super()
    this.state = { group: null }
  }

  componentDidMount() {
    API.type('groups')
      .get(this.props.match.params.group_id)
      .then(group => {
        this.setState({
          group
        })
      })

    API.type('subject_sets')
      .get({ group_id: this.props.match.params.group_id })
      .then(sets => {
        this.setState({
          subject_sets: sets
        })
      })
  }

  renderStats = (pending, finished, pendingText, finishedText, completionText) =>
    <dl className="stats-list">
      {pendingText && <div>
        <dt>{pendingText}</dt>
        <dd>
          {pending || 0}
        </dd>
      </div>}
      {finishedText && <div>
        <dt>{finishedText}</dt>
        <dd>
          {finished || 0}
        </dd>
      </div>}
      {completionText && <div className="completion">
        <dt>{completionText}</dt>
        <dd>
          {pending || finished ? parseInt((pending / (pending + finished)) * 100) : 0} %
        </dd>
      </div>}
    </dl>

  render() {
    if (this.state.group == null) {
      return (
        <div className="group-page">
          <h2>Loading...</h2>
        </div>
      )
    }
    const termsMap = this.props.context.project.terms_map
    let subjectsTerm = termsMap.subject
    subjectsTerm = pluralize(subjectsTerm[0].toUpperCase() + subjectsTerm.substring(1))

    // the number of pending and finished items by workflow
    const workflowCounts = (this.state.group.stats &&
      this.state.group.stats.workflow_counts &&
      this.props.context.project.workflows.map((workflow) => {
        return {
          workflow,
          counts: this.state.group.stats.workflow_counts[workflow.id]
        }
      }).filter(item => item.counts)) || []

    return (
      <div className="page-content">
        <div className="group-page">
          <div className="group-information">
            <dl className="metadata-list">
              {(() => {
		console.log("this.state =>", this.state);
                const result = []
                for (let k in this.state.group.meta_data) {
                  // Is there another way to return both dt and dd elements without wrapping?
                  const v = this.state.group.meta_data[k]
                  if (
                    [
                      'key',
                      'description',
                      'cover_image_url',
                      'external_url',
                      'retire_count'
                    ].indexOf(k) < 0
                  ) {
                    result.push(
                      <div key={k}>
                      </div>
                    )
                  }
                }

                return result
              })()}
              {this.state.group.meta_data.external_url != null &&
                <div>
                  <dt>External Resource</dt>
                  <dd>
                    <a
                      href={this.state.subject_sets[0].meta_data.source_url}
                      target="_blank"
                    >
	              Link to Data Source
                    </a>
                  </dd>
                </div>}
            </dl>
            <img
              className="group-image"
              src={this.state.group.cover_image_url}
            />
          </div>
        </div>
      </div>
    )
  }
}
