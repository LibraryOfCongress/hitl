import React from 'react'
import ReactDOM from 'react-dom'

import marked from '../lib/marked.min'

import GroupBrowser from './group-browser'
import { AppContext } from './app-context'

@AppContext
export default class CustomPage extends React.Component {
  componentDidMount() {
    const pattern = new RegExp('#/[A-z]*#(.*)')
    const selectedID = `${window.location.hash}`.match(pattern)

    if (selectedID) {
      $('.selected-content').removeClass('selected-content')

      $(`div#${selectedID[1]}`).addClass('selected-content')
      $(`a#${selectedID[1]}`).addClass('selected-content')
    }

    const elms = $(ReactDOM.findDOMNode(this)).find('a.about-nav')
    elms.on('click', function (e) {
      e.preventDefault()
      $('.selected-content').removeClass('selected-content')
      $(this).addClass('selected-content')

      const divId = $(this).attr('href')
      return $(divId).addClass('selected-content')
    })

    const el = $(ReactDOM.findDOMNode(this)).find('#accordion,.accordion')
    return el.accordion({
      collapsible: true,
      active: false,
      heightStyle: 'content'
    })
  }

  render() {
    const formatted_name = this.props.page.name.replace('_', ' ')
    return (
      <div className="page-content custom-page" id={`${this.props.page.name}`}>
        <h1>{formatted_name}</h1>
        <div dangerouslySetInnerHTML={{ __html: marked(this.props.page.content) }} />
        {this.props.page.group_browser != null && this.props.page.group_browser !== '' &&
          <div className="group-area">
            <GroupBrowser project={this.props.project} title={this.props.page.group_browser} />
          </div>}
        <div className="updated-at">Last Update {this.props.page.updated_at}</div>
      </div>
    )
  }
}
