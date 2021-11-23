import API from './api'
import Project from '../models/project'

export default {
  componentDidMount: () =>
    API.type('projects').get('current').then((result) =>
      this.setState({ project: new Project(result) }))
}
