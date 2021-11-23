class PasswordsController < Devise::PasswordsController
  respond_to :json

  def update
    self.resource = resource_class.reset_password_by_token(resource_params)
    yield resource if block_given?

    if resource.errors.empty?
      resource.unlock_access! if unlockable?(resource)
      flash_message = resource.active_for_authentication? ? :updated : :updated_not_active
      resource.after_database_authentication
      sign_in(resource_name, resource)
      render json: {messages: [flash_message]}, status: 204
    else
      render json: {errors: resource.errors}, status: 418
    end
  end
end
