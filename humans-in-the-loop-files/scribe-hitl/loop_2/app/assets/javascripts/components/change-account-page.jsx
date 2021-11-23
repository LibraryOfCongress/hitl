import React from 'react'
import { Redirect } from 'react-router-dom'
import classNames from 'classnames'
import { AppContext, requestUserFetch } from './app-context.jsx'
import { getCsrfHeaders } from '../lib/csrf'

@AppContext
export default class ChangeAccountPage extends React.Component {
  constructor() {
    super()
    this.state = {
      errors: {},
      messages: [],
      redirect: false,
      loading: false
    }

    this.changeAccount = this.changeAccount.bind(this)

    fetch('/current_email', { method: 'GET', headers: getCsrfHeaders() })
      .then(response => response.json())
      .then(result => {
        this.setState({ email: result.email })
      })
  }

  changeAccount(event) {
    event.preventDefault()
    const data = new FormData(event.target)
    const user = {}
    data.forEach((value, key) => { user[key] = value })
    this.setState({ loading: true })
    fetch('/users', {
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
    const user = this.props.context.user
    if (!user || !this.state.email) {
      return null
    }
    return <div className="page-content login-page">
      <h1>Change Account</h1>
      <div>
        <form onSubmit={this.changeAccount}>
          {this.state.messages.map((message, i) => <span key={i} className="error-message">{message}</span>)}
          <label>
            Name
            <input type="text" name="name" required autoComplete="name" defaultValue={user.name} />
          </label>
          {this.showErrors('name')}
          <label>
            Email
            <input type="email" name="email" required autoComplete="email" style={{ textTransform: 'lowercase' }} defaultValue={this.state.email} />
          </label>
          {this.showErrors('email')}
          <label>
            Current Password
            <input type="password" name="current_password" required autoComplete="current-password" />
          </label>
          {this.showErrors('current_password')}
          <p>
            <button className={classNames('major-button', { 'is-loading': this.state.loading })}> Change Account</button>
          </p>
        </form>
      </div>
    </div>
  }
}
