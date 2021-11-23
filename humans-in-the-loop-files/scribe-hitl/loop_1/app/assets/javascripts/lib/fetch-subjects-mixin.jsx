/*
 * decaffeinate suggestions:
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import API from './api.jsx'
import queryString from 'query-string'

export default {
  componentDidMount() {
    // Alex Hebing: if we are transcribing, we only want to fetch subjects after 
    // user has selected a subject set (i.e. source)
    if (this.getActiveWorkflow().name !== 'transcribe') {
      this.fetchSubjectsBasedOnProps()
    }
  },

  // Retrieve the subject set id from 1) query params, 2) props or 3) return null
  getSubjectId(query) {
    if (query.subject_set_id != null) {
      return query.subject_set_id
    } else if (this.props.match.params.subject_set_id) {
      return this.props.match.params.subject_set_id
    } else {
      return null
    }
  },

  fetchSubjectsBasedOnProps() {
    // Fetching a single subject?
    if (this.props.match.params.subject_id != null) {
      return this.fetchSubject(this.props.match.params.subject_id)

      // Fetching subjects by current workflow and optional filters:
    } else {
      let query = queryString.parse(this.props.location.search)
      // Gather filters by which to query subjects
      const params = {
        parent_subject_id: this.props.match.params.parent_subject_id,
        group_id: query.group_id != null ? query.group_id : null,
        subject_set_id: this.getSubjectId(query)
      }
      return this.fetchSubjects(params)
    }
  },

  orderSubjectsByY(subjects) {
    return subjects.sort((a, b) => {
      // If a is positioned vertically adjacent to b, then order by x:
      if (Math.abs(a.region.y - b.region.y) <= a.region.height / 2) {
        return a.region.x >= b.region.x ? 1 : -1
        // Otherwise just order by y:
      } else {
        return a.region.y >= b.region.y ? 1 : -1
      }
    })
  },

  // Fetch a single subject:
  fetchSubject(subject_id) {
    const request = API.type('subjects').get(subject_id)

    this.setState({
      subject: []
    })

    return request.then(subject => {
      this.setState(
        {
          subject_index: 0,
          subjects: [subject]
        },
        () => {
          if (this.fetchSubjectsCallback != null) {
            this.fetchSubjectsCallback()
          }
        }
      )
    })
  },

  fetchSubjects(params, callback) {
    const _params = $.extend(
      {
        workflow_id: this.getActiveWorkflow().id,
        limit: this.getActiveWorkflow().subject_fetch_limit
      },
      params
    )
    return API.type('subjects')
      .get(_params)
      .then(subjects => {
        if (subjects.length === 0) {
          this.setState({ noMoreSubjects: true })
        } else {
          this.setState({
            subject_index: 0,
            subjects: this.orderSubjectsByY(subjects),
            subjects_next_page: subjects[0].getMeta('next_page')
          })
        }

        // Does including instance have a defined callback to call when new subjects received?
        if (this.fetchSubjectsCallback != null) {
          return this.fetchSubjectsCallback()
        }
      })
  }
}
