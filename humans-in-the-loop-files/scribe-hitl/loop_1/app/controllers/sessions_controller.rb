class SessionsController < ApplicationController
  respond_to :json, :html

  def new
    respond_to do |format|
      format.json{render json: current_user}
      format.html{redirect_to root_url, :notice => "Signed in!"}
    end
  end

  def create
    if env["omniauth.auth"]
      user = User.from_omniauth(env["omniauth.auth"])
    else
      user = User.find_by_password(params[:email], params[:password])
    end

    if user
      sign_in(user)
      session[:user_id] = user.id
      respond_to do |format|
        format.json{render json: current_user}
        format.html{redirect_to root_url, :notice => "Signed in!"}
      end
    else
      respond_to do |format|
        # I'm a teapot: to indicate that login failed without going
        # full out on implementing 401 properly with some
        # authentication scheme.
        format.json{render json: {}, status: 418}
        format.html{redirect_to root_url, :notice => "Invalid login credentials!"}
      end
    end
  end

  def destroy
    # prevent the user from restoring the session
    # by re-using the old cookie value
    # https://github.com/heartcombo/devise/issues/3031
    current_user.invalidate_all_sessions!
    sign_out(current_user)

    respond_to do |format|
      format.json {render json: {notice: "Signed out!"}, status: 200}
      format.html {redirect_to root_url, :notice => "Signed out!"}
    end
  end

protected

  def auth_hash
    request.env['omniauth.auth']
  end
end
