import React from 'react'
import PropTypes from 'prop-types'
import { Subject } from 'rxjs'

const userFetchSubject = new Subject()

export const contextTypes = {
  project: PropTypes.object,
  onCloseTutorial: PropTypes.func.isRequired,
  user: PropTypes.object,
  groupId: PropTypes.string
}

export function AppContext(ComponentToWrap) {
  class AppContextComponent extends React.Component {
    static contextTypes = contextTypes;
    render() {
      return (
        <ComponentToWrap {...this.props} context={this.context} />
      )
    }
  }
  return AppContextComponent
}

export function requestUserFetch() {
  userFetchSubject.next()
}
export const userFetchObservable = userFetchSubject.asObservable()
