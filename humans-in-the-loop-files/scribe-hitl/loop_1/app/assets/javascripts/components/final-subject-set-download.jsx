import React from 'react'
import createReactClass from 'create-react-class'
import FetchProjectMixin from '../lib/fetch-project-mixin'
import GenericPage from './generic-page'

export default createReactClass({
  displayName: 'FinalSubjectSetDownload',

  mixins: [FetchProjectMixin],

  getInitialState: () => {
    return { project: null }
  },

  render: () => {
    if (!this.state.project) {
      return null
    }

    const data_nav = this.state.project.page_navs['data']

    return (<GenericPage key='final-subject-set-browser' title="Data Exports" nav={data_nav} current_nav="/#/data/download">
      {this.state.project.downloadable_data ?
        <div>
          <h3>Data Exports Not Available</h3>
          <p>Sorry, but public data exports are not enabled for this project yet.</p>
        </div>
        :
        <div>
          <h2>Download</h2>

          <p>Participants have made {this.state.project.classification_count.toLocaleString()} contributions to {this.state.project.title} to date. This project periodically builds a merged, anonymized dump of that data, which is made public here.</p>

          <p><a className="standard-button json-link" href="/data/latest" target="_blank">Download Latest Raw Data</a></p>

          <p>For help interpretting the data, see <a href="https://github.com/zooniverse/scribeAPI/wiki/Data-Exports#user-content-data-model" target="_blank">Scribe WIKI on Data Exports</a>.</p>

          <p>To browse past releases and/or to be notified when new releases are made, you may wish to subscribe to the <a href="/data.atom" target="_blank" title="ATOM Feed of Data Releases"><i className="fa fa-rss-square" /> ATOM Feed of Data Releases</a></p>

        </div>
      }
    </GenericPage>)
  }
})
