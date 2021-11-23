import React from 'react'
import { Redirect, NavLink } from 'react-router-dom'
import classNames from 'classnames'

import marked from '../lib/marked.min.js'
import { AppContext, requestUserFetch } from './app-context.jsx'
import { getCsrfHeaders } from '../lib/csrf'

@AppContext
export default class SignUpPage extends React.Component {
  constructor() {
    super()
    this.state = {
      message: null,
      redirect: false,
      loading: false
    }
    if (document.referrer) {
      const url = new URL(document.referrer)
      if (url.host === window.location.host) {
        this.state.target = url.pathname.endsWith('admin/signin') ? '/admin' : url.pathname
      }
    }

    this.signUp = this.signUp.bind(this)
  }

  signUp(event) {
    event.preventDefault()
    this.setState({ loading: true })
    const data = new FormData(event.target)
    const user = {}
    data.forEach((value, key) => { user[key] = value })
    fetch('/users', {
      method: 'POST',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        ...getCsrfHeaders()
      },
      body: JSON.stringify({ user })
    }).then((response) => {
      this.setState({ loading: false })
      if (response.status === 200) {
        requestUserFetch()
        // success: redirect to user page or target
        this.setState({ redirect: true })
      }
      return response.json()
    }).then((json) => {
      if (!this.state.redirect) {
        this.setState({ message: json.message || 'Invalid email or password, check your credentials and try again.' })
      }
    }).catch(() => {
      this.setState({ message: 'Problem occurred. Try again or contact the admin.' })
    })
  }

  render() {
    if (this.state.redirect) {
      if (this.state.target) {
        window.location = this.state.target
        return
      }
      return <Redirect to="/intro" />
    }

    const termsConditions = this.props.context.project.partials['terms-conditions']
    return <div className="page-content login-page">
      <h1>Sign Up</h1>
      <div>
        <form onSubmit={this.signUp}>
          {this.state.message && this.state.message.split('\n').map((message, i) => <span key={i} className="error-message">{message}</span>)}
          <label>
            Name
            <input type="text" name="name" required autoComplete="name" />
          </label>
          <label>
            Email
            <input type="email" name="email" required autoComplete="email" style={{ textTransform: 'lowercase' }} />
          </label>
          <label>
            Password
            <input type="password" name="password" required autoComplete="new-password" />
          </label>
          <label>
            Password Confirmation
            <input type="password" name="password_confirmation" required autoComplete="new-password" />
          </label>
          {termsConditions && <p dangerouslySetInnerHTML={{ __html: marked(termsConditions) }}></p>}
          <p>
            <button className={classNames('major-button', { 'is-loading': this.state.loading })}>Sign Up</button>
          </p>
          <p>
            <NavLink to="/forgot_password" className="forgot-password">
              Forgot your password?
            </NavLink>
          </p>
        </form>
      </div>
    </div>
  }
}
