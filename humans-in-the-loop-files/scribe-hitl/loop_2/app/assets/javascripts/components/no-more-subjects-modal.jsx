import React from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'
import { AppContext } from './app-context.jsx'
import DraggableModal from './draggable-modal'
import GenericButton from './buttons/generic-button'

@AppContext
export default class NoMoreSubjectsModal extends React.Component {
  static defaultProps = {
    header: 'Nothing more to do here'
  }
  static propTypes = {
    project: PropTypes.object.isRequired,
    header: PropTypes.string.isRequired,
    workflowName: PropTypes.string.isRequired
  }

  render = () => {
    $('html, body')
      .stop()
      .animate({ scrollTop: 0 }, 500)

    let next_workflow = this.props.project.workflowWithMostActives(this.props.workflowName),
      next_href = '/',
      next_label = 'Continue'

    if (next_workflow) {
      const groupId = this.props.context.groupId
      next_href = '/' + next_workflow.name + (groupId ? `?group_id=${groupId}` : '')
    } else if (this.props.project.downloadable_data) {
      next_href = '/data'
      next_label = 'Explore Data'
    }

    return <DraggableModal
      header={this.props.header}
      buttons={<GenericButton label={next_label} to={next_href} />}
    >
      {next_workflow ?
        <p>
          Currently, there are no {this.props.project.term('subject')}s for you to {this.props.workflowName}.
            Try <NavLink to={next_href}>{next_workflow.name.capitalize()}</NavLink> instead!
        </p>

        :
        <div>
          <p>There&#39;s nothing more to transcribe in {this.props.project.title}!!  🎉 🎉 🎉
          </p>
          <p>Thank you to all the amazing volunteers who worked on this project.</p>

          {this.props.project.downloadable_data &&
            <p>The {this.props.project.root_subjects_count.toLocaleString()} records can be explored via the <a href="/#/data">Data tab</a>.</p>
          }
        </div>

      }
    </DraggableModal>
  }
}
