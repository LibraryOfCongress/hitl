export default class User {
  constructor(data) {
    Object.assign(this, data)
  }

  /**
   * Implementation of user.rb:can_view_admin
   */
  get canViewAdmin() {
    return ['admin', 'team'].indexOf(this.role) > -1
  }
}
