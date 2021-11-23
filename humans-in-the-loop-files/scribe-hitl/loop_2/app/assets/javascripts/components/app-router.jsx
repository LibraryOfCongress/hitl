/*
 * decaffeinate suggestions:
 * DS101: Remove unnecessary use of Array.from
 * DS102: Remove unnecessary code created because of implicit returns
 * DS205: Consider reworking code to avoid use of IIFEs
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React from 'react'
import ReactDOM from 'react-dom'


import { App } from './app'
import { Route, Redirect, Switch } from 'react-router'
import { HashRouter } from 'react-router-dom'

import ChangeAccountPage from './change-account-page'
import ChangePasswordPage from './change-password-page'
import DeleteAccountPage from './delete-account-page'
import CustomPage from './custom-page'
import HomePage from './home-page'
import LoginPage from './login-page'
import SignUpPage from './sign-up-page'
import SignOut from './sign-out'
import ForgotPasswordPage from './forgot-password-page'
import UserPage from './user-page'

import Mark from './mark/index'
import Transcribe from './transcribe/index'
import Verify from './verify/index'

// TODO Group routes currently not implemented
import GroupPage from './group-page'
import GroupBrowser from './group-browser'
import FinalSubjectSetBrowser from './final-subject-set-browser'
import FinalSubjectSetPage from './final-subject-set-page'
import FinalSubjectSetDownload from './final-subject-set-download'

import Project from '../models/project'
import API from '../lib/api'

function getComponent(name) {
  switch (name) {
    case 'mark':
      return Mark
    case 'transcribe':
      return Transcribe
    case 'verify':
      return Verify
  }
}
export default class AppRouter {
  constructor() {
    API.type('projects')
      .get()
      .then(result => {
        window.project = new Project(result[0])
        this.runRoutes(window.project)
      })
  }

  runRoutes(project) {
    let w, i
    const routes = (
      <App>
        <Switch>
          <Redirect from="/home" to="/" />
          <Route exact name="home" path="/" component={HomePage} />
          <Route exact name="change_account" path="/change_account" component={ChangeAccountPage} />
          <Route exact name="change_password" path="/change_password/:reset_password_token?" component={ChangePasswordPage} />
          <Route exact name="delete_account" path="/delete_account" component={DeleteAccountPage} />
          <Route exact name="login" path="/login" component={LoginPage} />
          <Route exact name="sign_up" path="/sign_up" component={SignUpPage} />
          <Route exact name="sign_out" path="/sign_out" component={SignOut} />
          <Route exact name="forgot_password" path="/forgot_password" component={ForgotPasswordPage} />
          <Route exact name="user" path="/user" component={UserPage} />
          {(() => {
            const result = []
            for (w of Array.from(project.workflows)) {
              if (['mark', 'transcribe', 'verify'].includes(w.name)) {
                result.push(w)
              }
            }
            return result
          })().map((workflow, key) => {
            const component = getComponent(workflow.name)
            return (
              <Route
                exact
                key={key}
                path={'/' + workflow.name}
                component={component}
                name={workflow.name}
              />
            )
          })}
          {(() => {
            const result1 = []
            for (i = 0; i < project.workflows.length; i++) {
              w = project.workflows[i]
              if (['mark'].includes(w.name)) {
                result1.push(w)
              }
            }
            return result1
          })().map((workflow, key) => {
            const component = getComponent(workflow.name)
            return (
              <Route
                exact
                key={key}
                path={'/' + workflow.name + '/:subject_set_id' + '/:subject_id'}
                component={component}
                name={workflow.name + '_specific_subject'}
              />
            )
          })}
          {(() => {
            const result2 = []
            for (i = 0; i < project.workflows.length; i++) {
              w = project.workflows[i]
              if (['mark'].includes(w.name)) {
                result2.push(w)
              }
            }
            return result2
          })().map((workflow, key) => {
            const component = getComponent(workflow.name)
            return (
              <Route
                exact
                key={key}
                path={'/' + workflow.name + '/:subject_set_id'}
                component={component}
                name={workflow.name + '_specific_set'}
              />
            )
          })}
          {(() => {
            const result3 = []
            for (i = 0; i < project.workflows.length; i++) {
              w = project.workflows[i]
              if (['transcribe', 'verify'].includes(w.name)) {
                result3.push(w)
              }
            }
            return result3
          })().map((workflow, key) => {
            const component = getComponent(workflow.name)
            return (
              <Route
                exact
                key={key}
                path={'/' + workflow.name + '/:subject_id'}
                component={component}
                name={workflow.name + '_specific'}
              />
            )
          })}
          {(() => {
            const result4 = []
            for (i = 0; i < project.workflows.length; i++) {
              w = project.workflows[i]
              if (['transcribe'].includes(w.name)) {
                result4.push(w)
              }
            }
            return result4
          })().map((workflow, key) => {
            const component = getComponent(workflow.name)
            return (
              <Route
                exact
                key={key}
                path={'/' + workflow.name + '/:workflow_id' + '/:parent_subject_id'}
                component={component}
                name={workflow.name + '_entire_page'}
              />
            )
          })}
          {// Project-configured pages:
            project.pages != null && project.pages.map((page, key) => {
              return (
                <Route
                  exact
                  key={key}
                  path={'/' + page.key}
                  render={() => <CustomPage page={page} />}
                />
              )
            })
          }
          <Route
            path={`/${project.data_url_base}/browse`}
            component={FinalSubjectSetBrowser}
            name='final_subject_sets'
          />
          {project.downloadable_data &&
            <Route
              path={`/${project.data_url_base}/browse/:final_subject_set_id`}
              component={FinalSubjectSetPage}
              name='final_subject_set_page'
            />
          }
          <Route
            path={`/${project.data_url_base}/download`}
            component={FinalSubjectSetDownload}
            name='final_subject_sets_download'
          />
          <Route path="/groups/:group_id" component={GroupPage} name="group_show" />
          <Route path="/groups" component={GroupBrowser} name="groups" />
        </Switch>
      </App>
    )
    ReactDOM.render(<HashRouter>{routes}</HashRouter>, document.getElementById('app'))
    // return Router.run(routes, (Handler, state) =>
    //   React.render(<Handler />, document.body)
    // );
  }
}

$(document).ready(() =>
  new AppRouter())
