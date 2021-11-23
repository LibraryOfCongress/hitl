import React from 'react'
import createReactClass from 'create-react-class'
import API from '../lib/api'
import GenericPage from './generic-page'
import FetchProjectMixin from '../lib/fetch-project-mixin'

import FinalSubjectAssertion from './final-subject-assertion'


export default createReactClass({
  displayName: 'FinalSubjectSetPage',

  mixins: [FetchProjectMixin],

  getInitialState: () => ({
    set: null,
    tab: null,
    tabs: [],
  }),
  componentDidMount: () =>
    API.type("final_subject_sets").get(this.props.params.final_subject_set_id).then((set) => {
      const tabs = []
      if (set.export_document) tabs.push('export-doc')
      if (set.meta_data) tabs.push('source-metadata')
      tabs.push('assertions')
      this.setState({
        set: set,
        tab: tabs[0],
        tabs: tabs
      })
    }),
  showExportDoc: () =>
    this.showTab('export-doc'),

  showAssertions: () =>
    this.showTab('assertions'),

  showTab: (which) =>
    this.setState({ tab: which }),


  render: () => {
    if (!this.state.set || !this.state.project) return null

    const data_nav = this.state.project.page_navs[this.state.project.data_url_base]
    let display_field

    return <GenericPage key='final-subject-set-browser' title="Data Exports" nav={data_nav} current_nav={`/#/${this.state.project.data_url_base}/browse`}>
      <div className="final-subject-set-browser">
        <div className="final-subject-set-page">

          <a href={`/#/${this.state.project.data_url_base}/browse?keyword=${this.props.match.params.keyword}&field=${this.props.match.params.field || ''}`} className="back">Back</a>

          <a className="standard-button json-link" href={`/final_subject_sets/${this.state.set.id}.json`} target="_blank">Download Item Raw Data</a>
          {this.state.set.export_document && (display_field = this.state.set.export_document.export_fields[0]) ?
            <h2>{display_field.name} {display_field.value}</h2>
            :
            <h2>Record {this.state.set.id}</h2>
          }

          <img src={this.state.set.subjects[0].location.standard} className="standard-image" />

          {this.state.tabs.length > 1 &&
            <ul className="tabs">
              {this.state.tabs.indexOf('export-doc') >= 0 &&
                <li className={this.state.tab == 'export-doc' ? 'active' : ''}><a href="javascript:void(0);" onClick={this.showExportDoc}>Best Data</a></li>
              }
              <li className={this.state.tab == 'assertions' ? 'active' : ''}><a href="javascript:void(0);" onClick={this.showAssertions}>All Data</a></li>
              <li className={this.state.tab == 'source-metadata' ? 'active' : ''}><a href="javascript:void(0);" onClick={() => this.showTab('source-metadata')}>Source Metadata</a></li>
            </ul>
          }

          {this.state.tab == 'export-doc' && this.state.set.export_document &&
            <div>
              <p>These data points represent numerous individual classifications that have been merged and lightly cleaned up to adhere to {this.state.project.title}'s data model.</p>

              {this.state.set.export_document.export_fields.map((field, i) => {
                if (field.assertion_ids) {
                  let assertion = null, subject = null
                  for (let s of this.state.set.subjects) {
                    for (let a of s.assertions) {
                      if (field.assertion_ids.indexOf(a.id) >= 0) {
                        assertion = a
                        subject = s
                      }
                    }
                  }
                  if (assertion && subject)
                    return <div key={i}>
                      <FinalSubjectAssertion subject={subject} assertion={assertion} project={this.state.project} field={field} />
                    </div>
                }
              })
              }
            </div>
          }

          {this.state.tab == 'assertions' &&
            <div>
              <p>These data points represent all distinct assertions made upon this {this.props.project.term('subject set')} - without cleanup. Each assertion may represent several distinct contributions.</p>
              <ul>
                {this.state.set.subjects.map((subject) => {
                  // Sort assertions by ExportDocumentSpec field order:
                  const field_name_order = (this.props.project.export_document_specs[0].spec_fields.map((field) => field.name))
                  const assertions = subject.assertions.sort((a1, a2) => {
                    // If field name doesn't appear in spec, sort it last (i.e. index 1000):
                    const ord1 = field_name_order.indexOf(a1.name) >= 0 ? field_name_order.indexOf(a1.name) : 1000,
                      ord2 = field_name_order.indexOf(a2.name) >= 0 ? field_name_order.indexOf(a2.name) : 1000
                    return ord1 < ord2 ?
                      -1
                      :
                      1
                  })


                  return <li key={subject.id}>
                    <ul>
                      {assertions.filter(assertion => assertion.name).map((assertion, i) =>
                        <li key={i}>
                          <FinalSubjectAssertion subject={subject} assertion={assertion} project={this.props.project} />
                        </li>
                      )}
                    </ul>

                  </li>
                })}
              </ul>
            </div>
          }

          {this.state.tab == 'source-metadata' &&

            <div>
              <p>This metadata was imported alongside the source images at the beginning of the project and may include high res source URIs and processing details.</p>

              <dl className="source-metadata">
                {this.state.set.meta_data.map((k, v) =>
                  <div key={k}>
                    <dt>{k.split('_').map((v) => v.capitalize()).join(' ')}</dt>
                    {v.match(/https?:\/\//) ?
                      <dd><a href={v} target="_blank">{v}</a></dd>
                      :
                      <dd>{v}</dd>
                    }
                  </div>
                )}
              </dl>
            </div>
          }
        </div>
      </div>
    </GenericPage>
  }
})
