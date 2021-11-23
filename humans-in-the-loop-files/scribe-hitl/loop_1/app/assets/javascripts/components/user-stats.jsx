import React from 'react'
import { NavLink } from 'react-router-dom'
import pluralize from 'pluralize'

import { AppContext } from './app-context'
import { parseTitle } from './subject-set-selector'
import { getCsrfHeaders } from '../lib/csrf'

@AppContext
export default class UserStats extends React.Component {
  constructor() {
    super()
    this.state = { stats: null }
  }

  componentDidMount() {
    fetch('/user_stats', { headers: getCsrfHeaders() })
      .then(response => response.json())
      .then(stats => this.setState({ stats }))
  }

  render() {
    if (!this.state.stats) {
      return (
        <div className="user-stats">
          <h2>Loading...</h2>
        </div>
      )
    }
    const termsMap = this.props.context.project.terms_map
    const subjectSetTerm = termsMap['subject set']
    const subjectSetsTerm = pluralize(subjectSetTerm[0].toUpperCase() + subjectSetTerm.substring(1))

    const stats = this.state.stats
    const workflows = this.props.context.project.workflows
    const showWorkflows = [
      workflows.find(workflow => workflow.name == 'mark'),
      workflows.find(workflow => workflow.name == 'transcribe')]

    if (Object.keys(stats).length == 0) {
      return <div className="user-stats">
        <h2>Contribution Statistics</h2>
        <p>
          You will find an overview of your contributions on this page.
        </p>
        <NavLink className="major-button" to="/intro">Get Started!</NavLink>
      </div>
    }

    return <div className="user-stats">
      <h2>Contribution Statistics</h2>
      <table>
        <thead>
          <tr>
            <th>{subjectSetsTerm}</th>
            <th>Placed Markings</th>
            <th>{termsMap.transcribe_finished}</th>
          </tr>
        </thead>
        <tbody>
          {
            Object.keys(stats)
              .sort((a, b) => {
                const left = stats[a].key.toUpperCase(),
                  right = stats[b].key.toUpperCase()

                if (left > right) {
                  return 1
                } else if (left < right) {
                  return -1
                }
                return 0
              })
              .map((subjectSetId) => {
                const workflowCounts = stats[subjectSetId]
                return <tr key={subjectSetId}>
                  <th>{parseTitle(workflowCounts.key)}</th>
                  {showWorkflows.map((workflow) =>
                    <td key={workflow.id}>
                      {workflowCounts[workflow.id] || 0}
                    </td>)}
                </tr>
              })
          }
        </tbody>
      </table>
      <em className="thank-you">Thank you for your contributions!</em>
    </div>
  }
}
