class RegistrationsController < Devise::RegistrationsController
  before_filter :update_sanitized_params, if: :devise_controller?

  respond_to :json

  # POST /users
  def create
    # http://www.artechspot.com/blog/customize-devise-sing-in-and-sign-up-to-respond-in-json
    build_resource(sign_up_params)
    resource.email.downcase!
    resource.save
    yield resource if block_given?
    if resource.persisted?
      if resource.active_for_authentication?
        set_flash_message :notice, :signed_up if is_flashing_format?
        #find_message is devise method. We used for json response
        msg = find_message(:signed_up, {})
        sign_up(resource_name, resource)
        respond_with(resource) do |format|
          format.json { render json: {url: after_sign_up_path_for(resource)}, status: 200 }
        end
      else
        set_flash_message :notice, :"signed_up_but_#{resource.inactive_message}" if is_flashing_format?
        #find_message is devise method. We used for json response
        msg = find_message(:"signed_up_but_#{resource.inactive_message}", {})
        expire_data_after_sign_in!
        respond_with(resource) do |format|
          format.json { render json: {message: msg, url: after_inactive_sign_up_path_for(resource)}, status: 200 }
        end
      end
    else
      clean_up_passwords resource
      #passing block to handle error in signup for json
      #http://edgeapi.rubyonrails.org/classes/ActionController/Responder.html
      respond_with(resource) do |format|
        msg = resource.errors.full_messages.join("\n")
        format.json { render json: {message: msg}, status: 401 }
      end
    end
  end
  
  def update_sanitized_params
    devise_parameter_sanitizer.permit(:sign_up, keys: [:name, :email, :password, :password_confirmation])
    devise_parameter_sanitizer.permit(:account_update, keys: [:name, :email, :password, :password_confirmation, :current_password])
  end

end
