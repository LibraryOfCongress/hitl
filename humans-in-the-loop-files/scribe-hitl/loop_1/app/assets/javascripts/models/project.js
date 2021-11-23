export default class Project {
  constructor(obj) {
    for (let k in obj) {
      const v = obj[k]
      this[k] = v
    }
    this.data_url_base = 'data_new'
  }

  term(t) {
    return this.terms_map[t] != null ? this.terms_map[t] : t
  }

  workflowWithMostActives(not_named = '') {
    return this.mostActiveWorkflows().filter(w => w.name != not_named)[0]
  }

  mostActiveWorkflows() {
    return this.workflows.filter((w) => w.active_subjects > 0).sort((w1, w2) =>
      w1.active_subjects > w2.active_subjects ? -1 : 1)
  }
}