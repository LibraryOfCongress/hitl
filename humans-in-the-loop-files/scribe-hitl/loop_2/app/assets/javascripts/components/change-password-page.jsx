import React from 'react'
import { Redirect } from 'react-router-dom'
import classNames from 'classnames'
import { AppContext, requestUserFetch } from './app-context.jsx'
import { getCsrfHeaders } from '../lib/csrf'

@AppContext
export default class ChangePasswordPage extends React.Component {
  constructor() {
    super()
    this.state = {
      errors: {},
      messages: [],
      redirect: false,
      loading: false
    }

    this.changePassword = this.changePassword.bind(this)
  }

  changePassword(event) {
    event.preventDefault()
    const data = new FormData(event.target)
    const user = {}
    data.forEach((value, key) => { user[key] = value })
    this.setState({ loading: true })
    fetch(user['reset_password_token'] ? '/users/password' : '/users', {
      method: 'PATCH',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...getCsrfHeaders()
      },
      body: JSON.stringify({ user })
    }).then((response) => {
      requestUserFetch()
      this.setState({ loading: false })
      if (response.status === 204) {
        // success: redirect to home or target
        this.setState({ redirect: true })
      } else {
        return response.json()
      }
    }).then((payload) => {
      if (payload) {
        this.setState({
          errors: payload.errors,
          messages: payload.messages || []
        })
      }
    }).catch(() => {
      this.setState({ messages: ['Problem occurred. Try again or contact the admin.'] })
    })
  }

  showErrors(name) {
    return this.state.errors && this.state.errors[name] && <span className="error-message">{this.state.errors[name].join(<br />)}</span>
  }

  render() {
    if (this.state.redirect) {
      if (this.state.target) {
        window.location = this.state.target
        return
      }
      return <Redirect to="/user" />
    }

    const reset_password_token = this.props.match.params.reset_password_token
    return <div className="page-content login-page">
      <h1>Change Password</h1>
      <div>
        <form onSubmit={this.changePassword}>
          {this.state.messages.map((message, i) => <span key={i} className="error-message">{message}</span>)}
          <label>
            Current Password
            {(reset_password_token && <input type="password" name="reset_password_token" value={reset_password_token} readOnly={true} autoComplete="off" />) ||
              <input type="password" name="current_password" required autoComplete="current-password" />}
          </label>
          {this.showErrors('current_password')}
          {this.showErrors('reset_password_token')}
          <label>
            New Password
            <input type="password" name="password" required autoComplete="new-password" />
          </label>
          {this.showErrors('password')}
          <label>
            Password Confirmation
            <input type="password" name="password_confirmation" required autoComplete="new-password" />
          </label>
          {this.showErrors('password_confirmation')}
          <p>
            <button className={classNames('major-button', { 'is-loading': this.state.loading })}> Change Password</button>
          </p>
        </form>
      </div>
    </div>
  }
}
