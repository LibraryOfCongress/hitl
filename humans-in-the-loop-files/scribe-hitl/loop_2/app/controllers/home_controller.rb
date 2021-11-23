class HomeController < ApplicationController
  # The view needs to be rerendered to update the CSRF meta tag
  caches_action :index, :layout => false, :cache_path => "home/index"

  def index
  end
end
