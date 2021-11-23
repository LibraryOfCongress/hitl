/*
 * decaffeinate suggestions:
 * DS101: Remove unnecessary use of Array.from
 * DS104: Avoid inline assignments
 * DS205: Consider reworking code to avoid use of IIFEs
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import API from './api.jsx'
import queryString from 'query-string'

export default {
  fetchSubjectSetsBasedOnProps() {
    // Establish a callback for after subjects are fetched - to apply additional state changes:
    const postFetchCallback = subject_sets => {
      if (subject_sets.length === 0) {
        return
      }

      const state = {}
      let query = queryString.parse(this.props.location.search)
      // If a specific subject id indicated..
      if (query.selected_subject_id != null) {
        // Get the index of the specified subject in the (presumably first & only) subject set
        let index
        state.subject_index = (index = subject_sets[0].subjects.findIndex((subj) => subj.id === query.selected_subject_id)) && index > 0
          ? index
          : 0
      }

      // If taskKey specified, now's the time to set that too:
      if (query.mark_task_key) {
        state.taskKey = query.mark_task_key
      }

      if (state) {
        this.setState(state)
      }
    }

    let query = queryString.parse(this.props.location.search)
    // Fetch by subject-set id?
    const subject_set_id =
      this.props.match.params.subject_set_id != null
        ? this.props.match.params.subject_set_id
        : query.subject_set_id
    if (subject_set_id != null) {
      this.setState({
        selectSubjectSet: false
      })
      this.fetchSubjectSet(subject_set_id, postFetchCallback)

      // Fetch subject-sets by filters:
    } else {
      // Gather filters by which to query subject-sets
      const params = {
        group_id: query.group_id != null ? query.group_id : null
      }
      this.fetchSubjectSets(params, postFetchCallback)
    }
  },

  // this method fetches the next page of subjects in a given subject_set.
  // right now the trigger for this method is the forward or back button in the light-box
  // I am torn about whether to set the subject_index at this point? -- AMS
  // fetchNextSubjectPage: (page_number, callback_fn) ->

  // Gather filters by which to query subject-sets
  // params =
  //  subject_set_id: subject_set_id
  //  workflow_id: workflow_id
  //  subject_page: page_number

  // @fetchSubjectSets params, () =>
  //  @setState subject_index: subject_index
  // callback_fn()

  orderSubjectsByOrder(subject_sets) {
    for (let subject_set of Array.from(subject_sets)) {
      subject_set.subjects = subject_set.subjects.sort(function (a, b) {
        if (a.order >= b.order) {
          return 1
        } else {
          return -1
        }
      })
    }
    return subject_sets
  },

  // Fetch a single subject-set (i.e. via SubjectSetsController#show)
  // Query hash added to prevent local mark from being re-transcribable.
  fetchSubjectSet(subject_set_id, callback) {
    const request = API.type('subject_sets').get(subject_set_id, {})

    request.then(set => {
      this.setState({ subjectSets: [set] }, () => {
        this.fetchSubjectsForCurrentSubjectSet(1, null, callback)
      })
    })
  },

  // This is the main fetch method for subject sets. (fetches via SubjectSetsController#index)
  fetchSubjectSets(params, callback) {
    params = $.extend({ workflow_id: this.getActiveWorkflow().id }, params)

    // Apply defaults to unset params:
    const _params = $.extend(
      {
        limit: 25,
        workflow_id: this.getActiveWorkflow().id,
        random: true
      },
      params
    )
    // Strip null params:
    params = {}
    for (let k in _params) {
      const v = _params[k]
      if (v != null) {
        params[k] = v
      }
    }

    API.type('subject_sets')
      .get(params)
      .then(sets => {
        if (sets.length === 0)
          this.setState({ noMoreSubjectSets: true })
        else
          this.setState({ subjectSets: sets }, () => {
            if (this.getActiveWorkflow().name.toLowerCase() !== 'transcribe') {
              this.fetchSubjectsForCurrentSubjectSet(1, null, callback)
            }
          })
      })
  },

  // PB: Setting default limit to 120 because it's a multiple of 3 mandated by thumb browser
  // Changed it to 3 because getting 120 is slow
  fetchSubjectsForCurrentSubjectSet(page = null, limit = null, callback = undefined, minSubjectOrder = 0) {
    if (this.state.selectSubjectSet) {
      // selecting a subject set, don't retrieve anything yet
      return
    }
    if (page == null) {
      page = 1
    }
    if (limit == null) {
      limit = 3
    }
    const ind = this.state.subject_set_index
    const sets = this.state.subjectSets

    // page & limit not passed when called this way for some reason, so we have to manually construct query:
    // sets[ind].get('subjects', {page: page, limit: limit}).then (subjs) =>
    // Alex Hebing: changed status to active here, because we don't want 'retired' subjects to appear,
    // even if opening the 'Mark' page from a subject set on the 'Home' page. (I.e. we always want only 'active' subjects.)
    const params = {
      subject_set_id: sets[ind].id,
      page,
      limit,
      min_subject_order: minSubjectOrder,
      type: 'root',
      status: 'active'
    }

    const activeWorkflow = this.getActiveWorkflow()
    if (activeWorkflow) {
      params['workflow_id'] = activeWorkflow.id
    }

    const process_subjects = subjs => {
      sets[ind].subjects = subjs
      const noMoreSubjects = !subjs || subjs.length == 0
      this.setState(
        {
          noMoreSubjects,
          subjectSets: sets,
          subjects_current_page: noMoreSubjects ? 0 : subjs[0].getMeta('current_page'),
          subjects_total_pages: noMoreSubjects ? 0 : subjs[0].getMeta('total_pages')
        },
        () => {
          typeof callback === 'function' ? callback(sets) : undefined
        }
      )
    }

    // Couldn't get this code to work with the changes. Commenting for now. --STI
    // # Since we're fetching by query, json-api-client won't cache it, so let's cache it lest we re-fetch subjects everytime something happens:
    // @_subject_queries ||= {}
    // console.log '@_subject_queries[params] = ', @_subject_queries[params]
    // if (subjects = @_subject_queries[params])?
    //   process_subjects subjects
    //
    // else

    if (!this._subject_queries) {
      this._subject_queries = {}
    }
    return API.type('subjects')
      .get(params)
      .then(subjects => {
        this._subject_queries[params] = subjects
        process_subjects(subjects)
      })
  },

  // used by "About this {group}" link on Mark interface
  fetchGroups() {
    return API.type('groups')
      .get({ project_id: this.props.context.project.id })
      .then(groups => {
        for (let group of Array.from(groups)) {
          group.showButtons = false
        } // hide buttons by default
        this.setState({ groups })
      })
  }
}
