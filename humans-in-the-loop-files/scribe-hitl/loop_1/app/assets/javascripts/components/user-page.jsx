import React from 'react'
import { NavLink } from 'react-router-dom'

import { AppContext } from './app-context'
import UserStats from './user-stats'

@AppContext
export default class UserPage extends React.Component {
  constructor() {
    super()
    this.state = { stats: null }
  }

  render() {
    const user = this.props.context.user
    if (!user) {
      return <div className="user-page">
        <div className="page-content">
          <h1>Login to View This Page</h1>
          <div>
            <p>You need to be logged in to view your information.</p>
            <NavLink to="/login" className="major-button">Login</NavLink>
            <p>
              <NavLink to="/sign_up">Create a New Account</NavLink>
            </p>
          </div>
        </div>
      </div>
    }

    return (
      <div className="user-page">
        <div className="page-content">
          <h1>User Page of <em>{user.name}</em></h1>
          <div>
            <table>
              <tbody>
                <tr>
                  <th>Name</th><td>{user.name}</td>
                </tr>
                <tr>
                  <th>Role</th><td>{user.role}</td>
                </tr>
                <tr>
                  <th>Signed Up</th><td>{user.created_at}</td>
                </tr>
                <tr>
                  <th>Login Count</th><td>{user.sign_in_count}</td>
                </tr>
              </tbody>
            </table>
            <p>
              <NavLink to="/change_account" className="major-button">Change Name / Email</NavLink>&nbsp;
              <NavLink to="/change_password" className="major-button">Change Password</NavLink>
            </p>
            <p>
              <NavLink to="/delete_account">Delete account</NavLink>
            </p>
          </div>
          <UserStats />
        </div>
      </div>
    )
  }
}
