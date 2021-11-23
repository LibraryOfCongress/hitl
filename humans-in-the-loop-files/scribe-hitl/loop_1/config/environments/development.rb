API::Application.configure do
  # Settings specified here will take precedence over those in config/application.rb.
  # In the development environment your application's code is reloaded on
  # every request. This slows down response time but is perfect for development
  # since you don't have to restart the web server when you make code changes.
  config.cache_classes = false

  # Do not eager load code on boot.
  config.eager_load = false

  # Show full error reports and disable caching.
  config.consider_all_requests_local       = true
  config.action_controller.perform_caching = false

  # Don't care if the mailer can't send.
  config.action_mailer.raise_delivery_errors = false
  config.action_mailer.default_url_options = { :host => ENV["DOMAIN_NAME"] || 'localhost:3000' }

  # Print deprecation notices to the Rails logger.
  config.active_support.deprecation = :log


  # Debug mode disables concatenation and preprocessing of assets.
  # This option may cause significant delays in view rendering with a large
  # number of complex assets.
  config.assets.debug = true
  # config.relative_url_root = "/workflow-1" 

  config.action_mailer.smtp_settings = {
    address: ENV["MAIL_ADDRESS"] || "smtp.gmail.com",
    port: (ENV["MAIL_PORT"] || "587").to_i,
    domain: ENV["DOMAIN_NAME"],
    authentication: ("plain" if (ENV["MAIL_USERNAME"] || ENV["GMAIL_USERNAME"]).present?),
    enable_starttls_auto: (ENV["MAIL_TTLS"] || "true") != "false",
    user_name: (ENV["MAIL_USERNAME"] || ENV["GMAIL_USERNAME"]).presence,
    password: (ENV["MAIL_PASSWORD"] || ENV["GMAIL_PASSWORD"]).presence
  }
  # Send email in development mode.
  config.action_mailer.perform_deliveries = true
end
