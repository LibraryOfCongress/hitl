import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import createReactClass from 'create-react-class'
import FetchProjectMixin from '../lib/fetch-project-mixin'

export default createReactClass({
  displayName: 'GenericPage',

  mixins: [FetchProjectMixin],

  getInitialState: () => ({
    project: null
  }),
  getDefaultProps: () => ({
    key: null,
    title: null,
    content: null,
    nav: null,
    footer: null,
    current_nav: location.hash
  }),
  propTypes: {
    title: PropTypes.string,
    content: PropTypes.string,
    nav: PropTypes.string,
    footer: PropTypes.string
  },
  // Returns true if given nav link href appears to link to this page
  isCurrentNavLink: (href) => {
    // Known limitation: This will will assume equivalency of two URLs that don't have hashes
    // But use of the nav assumes hashes. A nav item really shouldn't link to a different domain/ctrl endpoint
    return href.replace(/.*#/, '') == this.props.current_nav.replace(/.*#/, '')
  },
  componentDidMount: () => {
    // Find nav link matching this.props.current_nav
    const matching = $(ReactDOM.findDOMNode(this)).find('.custom-page-nav li a').filter(el => this.isCurrentNavLink($(el).attr('href')))
    if (matching.length > 0) $(matching[0]).parent('li').addClass('current')
  },
  htmlContent: () => {
    let content = this.props.content,
      project = this.state.project

    const replacements = {
      'project.classification_count': project && project.classification_count || '__',
      'project.latest_export.created_at': project && project.latest_export && project.latest_export.created_at || '__',
      'project.root_subjects_count': project && project.root_subjects_count || '__',
      'project.title': project && project.title || '__'
    }
    for (let pattern of Object.keys(replacements)) {
      let replacement = replacements[pattern]
      pattern = new RegExp(`{{${pattern}}}`, 'gi')

      // assume, if it's an int, we want to comma format it:
      if (typeof (replacement) == 'number')
        replacement = replacement.toLocaleString()
      // If it's a date, parse it and make it human:
      if (replacement.match(/^\d{4}-\d{2}/))
        replacement = moment(replacement, moment.ISO_8601).calendar()

      content = content.replace(pattern, replacement)
    }
    return marked(content)
  },
  render: () =>
    <div className="page-content custom-page" id="#{this.props.key}">
      <h1>{this.props.title}</h1>
      <div className="custom-page-inner-wrapper #{ if this.props.nav? then 'with-nav' else '' }">
        {this.props.nav &&
          <div ref="nav" className="custom-page-nav" dangerouslySetInnerHTML={{ __html: marked(this.props.nav) }} />
        }
        {this.props.content &&
          <div className="custom-page-body" dangerouslySetInnerHTML={{ __html: this.htmlContent() }} />
        }
        {this.props.children}
      </div>
      <div className="updated-at">{this.props.footer}</div>
    </div>
})
