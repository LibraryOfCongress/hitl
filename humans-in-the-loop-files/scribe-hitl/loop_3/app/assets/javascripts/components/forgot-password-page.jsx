import React from 'react'
import { NavLink } from 'react-router-dom'
import classNames from 'classnames'
import { AppContext, requestUserFetch } from './app-context'
import { getCsrfHeaders } from '../lib/csrf'

@AppContext
export default class ForgotPasswordPage extends React.Component {
  constructor() {
    super()
    this.state = {
      message: null,
      success: false,
      loading: false
    }
    if (document.referrer) {
      const url = new URL(document.referrer)
      if (url.host === window.location.host) {
        this.state.target = url.pathname.endsWith('admin/signin') ? '/admin' : url.pathname
      }
    }

    this.forgotPassword = this.forgotPassword.bind(this)
  }

  forgotPassword(event) {
    event.preventDefault()
    const data = new FormData(event.target)
    this.setState({ loading: true })
    fetch('/users/password', {
      method: 'POST',
      headers: getCsrfHeaders(),
      body: data,
    }).then((response) => {
      requestUserFetch()
      this.setState({ loading: false })
      if (response.status === 201) {
        // success: redirect to home or target
        this.setState({
          message: 'A mail with reset instructions has been sent. Check your spam box if it isn\'t in your inbox.',
          success: true
        })
      } else {
        // invalid credentials: show message
        this.setState({
          message: 'Invalid email, check your address or create a new account.',
          success: false
        })
      }
    }).catch(() => {
      this.setState({
        message: 'Problem occurred. Try again or contact the admin.',
        success: false
      })
    })
  }

  render() {
    return <div className="page-content login-page">
      <h1>Reset Password</h1>
      <div>
        <form onSubmit={this.forgotPassword}>
          {this.state.message && <span className={this.state.success ? 'success-message' : 'error-message'}>{this.state.message}</span>}
          <label>
            Email
            <input type="email" name="user[email]" required autoComplete="email" />
          </label>
          <p>
            <button className={classNames('major-button', { 'is-loading': this.state.loading })}>Send Reset Instructions</button>
          </p>
        </form>
        <p>
          <NavLink to="/login">
            Login
          </NavLink>
          &nbsp;
          <NavLink to="/sign_up">
            Create a new account
          </NavLink>
        </p>
      </div>
    </div>
  }
}
