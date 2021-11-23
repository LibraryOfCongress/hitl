import React from 'react'
import createReactClass from 'create-react-class'
import qs from 'query-string'

import API from '../lib/api'
import LoadingIndicator from './loading-indicator'
import Pagination from './pagination'
import GenericPage from './generic-page'
import FetchProjectMixin from '../lib/fetch-project-mixin'

export default createReactClass({
  displayName: 'FinalSubjectSetBrowser',

  mixins: [FetchProjectMixin],

  getInitialState: () => ({
    entered_keyword: this.props.match.params.keyword,
    selected_field: this.props.match.params.field,
    searched_query: {},
    fetching_keyword: null,
    current_page: this.props.match.params.page || 1,
    more_pages: false,
    results: [],
    project: null
  }),

  componentDidMount: () => {
    this.checkQueryString()
  },

  componentWillReceiveProps: (new_props) => {
    this.checkQueryString(new_props)
  },

  checkQueryString: (props = this.props) => {
    if (props.query.keyword) {
      this.fetch({ keyword: props.query.keyword, field: props.query.field }, props.query.page)
    }
  },

  fetch: (query, page = 1) => {
    if (!this.isMounted()) return

    if (query.keyword != this.state.searched_keyword || query.field != this.state.selected_field || this.props.current_page != page) {
      let results = this.state.results
      if ((this.state.searched_query && this.state.searched_query.keyword) != query.keyword)
        results = []
      this.setState({ fetching_keyword: query.keyword, fetching_page: page, results: results }, () => {
        const per_page = 20,
          params = {
            keyword: query.keyword,
            field: query.field,
            per_page: per_page,
            page: this.state.fetching_page
          }
        API.type('final_subject_sets').get(params).then((sets) => {
          this.setState({
            results: sets,
            searched_query: {
              keyword: this.props.match.params.keyword,
              field: this.props.match.params.field
            },
            current_page: page,
            fetching_page: null,
            more_pages: sets && sets[0] && sets[0].getMeta('next_page'),
            fetching_keyword: null
          })
        })
      })
    }
  },

  handleKeyPress: (e) => {
    if (this.isMounted() &&
      [13].indexOf(e.keyCode) >= 0) // ENTER:
      this.search(e.target.value)
  },
  search: () => {
    let keyword = this.state.entered_keyword, // refs.search_input?.getDOMNode().value.trim() unless keyword?
      field = this.state.selected_field // this.refs.search_field?.getDOMNode().value.trim()

    this.context.router.history.push('/final_subject_sets?' + qs.stringify({ keyword: keyword, field: field }))
  },

  loadMore: () => {
    this.fetch(this.state.searched_query, this.state.current_page + 1)
  },

  handleChange: (e) =>
    this.setState({ entered_keyword: e.target.value }),

  handleFieldSelect: (e) =>
    this.setState({ selected_field: e.target.value }),

  renderPagination: () => {
    const result = this.state.results[0]
    const getMeta = (key) => result && result(key) || 0
    return (<Pagination
      total_pages={getMeta('total_pages')}
      current_page={getMeta('current_page')}
      next_page={getMeta('next_page')}
      prev_page={getMeta('prev_page')}
      onClick={this.goToPage}
    />)
  },

  renderSearch: () => {
    const docSpecs = this.state.project.export_document_specs && this.state.project.export_document_specs[0]
    return (<div>
      <p>Preview the data by searching by keyword below:</p>
      <form>
        {docSpecs && docSpecs.spec_fields &&
          <select ref="search_field" value={this.state.selected_field} onChange={this.handleFieldSelect}>
            <option value="">All Fields</option>
            {docSpecs.spec_fields.filter((field) => typeof (field.format) == 'string').map(field =>
              <option key={field.name} value={field.name}>{field.name}</option>)}
          </select>
        }
        <div>
          <input id="data-search" type="text" placeholder="Enter keyword" ref="search_input" value={this.state.entered_keyword} onChange={this.handleChange} onKeyDown={this.handleKeyPress} />
          <button className="standard-button" onClick={this.search}>Search</button>
        </div>
      </form>

      {(this.state.fetching_keyword && <LoadingIndicator fixed={true} />) ||
        (this.state.searched_query && this.state.searched_query.keyword && this.state.results.length == 0 &&
          <p>No matches yet for "{this.state.searched_query.keyword}"</p>) ||
        (this.state.results.length > 0 &&
          <div>
            <p>Found {this.state.results[0].getMeta('total')} matches</p>

            <ul className="results">
              {this.state.results.map((set) => {
                const url = `/#/${this.state.project.data_url_base}/browse/${set.id}?keyword=${this.state.searched_query.keyword}&field=${this.state.searched_query.field || ''}`,
                  matches = []

                let safe_keyword = (this.state.searched_query.keyword.toLowerCase().replace(/"/g, '').split(' ').map(w => w.replace(/\W/g, '\\$&'))).join('|')
                safe_keyword = (safe_keyword).join(',?')
                let regex = new RegExp(`(${safe_keyword})`, 'gi')

                // If a specific field searched, always show that:
                if (this.state.searched_query && this.state.searched_query.field) {
                  const term = (set.search_terms_by_field[this.state.searched_query.field] || []).join('; ')
                  if (term) {
                    matches.push({ field: this.state.searched_query.field, term: term })
                  }
                }
                // Otherwise show all fields that match
                else {
                  for (let k of set.search_terms_by_field) {
                    for (let v in set.search_terms_by_field[k].filter((v) => v.match(regex))) {
                      matches.push({ field: k, term: v })
                    }
                  }
                }
                return (
                  <li key={set.id}>
                    <div className="image">
                      <a href={url}>
                        <img src={set.subjects[0] && set.subjects[0].location.thumbnail} />
                      </a>
                    </div>
                    <div className="matches">
                      {matches.slice(0, 2).map((m, i) =>
                        (<div key={i} className="match">
                          <a href={url}>
                            <span className="field">{m.field}</span>
                            <span className="term" dangerouslySetInnerHTML={{ __html: m.term.truncate(100).replace(regex, '<em>$1</em>') }} />
                          </a>
                        </div>))
                      }
                    </div>
                  </li>)
              })
              }
            </ul>

            {this.state.results.length > 0 && this.renderPagination()}
          </div>)
      }
    </div>)
  },

  render: () => {
    if (!this.state.project)
      return null

    const data_nav = this.state.project.page_navs[this.state.project.data_url_base]

    return (<GenericPage key='final-subject-set-browser' title="Data Exports" nav={data_nav} current_nav={`/#/${this.state.project.data_url_base}/browse`}>
      <div className="final-subject-set-browser">

        <h2>Browse</h2>

        {!this.state.project.downloadable_data &&
          <div>
            <h3>Data Exports Not Available</h3>
            <p>Sorry, but public data exports are not enabled for this project yet.</p>
          </div>
          ||
          <div>
            {!(this.state.searched_query && this.state.searched_query.keyword) &&
              <p>Participants have made {this.state.project.classification_count.toLocaleString()} contributions to {this.state.project.title} to date. This project periodically builds a merged, anonymized dump of that data, which is made public here.</p>
            }

            {this.renderSearch()}

          </div>
        }
      </div>
    </GenericPage>)
  }
})
