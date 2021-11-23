source 'https://rubygems.org'

ruby '>= 2.2.10', '< 2.6.0'

gem 'rails', '~> 4.2', '>= 4.2.11.3'
gem 'sass-rails'
gem 'webpacker', '~> 4.x'
gem 'turbolinks'
gem 'jbuilder', '~> 1.2'
gem 'devise', '4.7.1'
gem 'omniauth-facebook'
gem "omniauth-google-oauth2"
gem 'omniauth-zooniverse', '~> 0.0.3'

gem 'mongoid', '~> 5.4.0'
gem 'active_model_serializers'
gem 'mongoid-serializer'
gem 'rack-cors', :require => 'rack/cors'
gem "bson"
gem "moped"

gem 'rack-streaming-proxy', '~> 2.0.1'
gem 'kaminari'
gem 'kaminari-mongoid'
gem 'fastimage', '1.7.0'

gem 'actionpack-action_caching'

gem 'newrelic_rpm'
gem 'newrelic_moped'

gem 'puma', '~> 3.12.6'

gem 'logstasher', '~> 1.3'

gem 'aws-sdk', '~> 2'
gem 'write_xlsx'
# gem 'mongoid_fulltext'

group :development do
  gem 'dotenv-rails'
end

group :development, :production do
  gem 'better_errors'
  gem 'binding_of_caller', :platforms=>[:mri_19, :mri_20, :rbx]
  gem 'quiet_assets'
  gem 'rails_layout'
end

group :test do
  gem 'capybara'
  gem 'cucumber-rails', :require=>false
  gem 'database_cleaner', '1.0.1'
  gem 'rspec-rails', '~> 3.6'
  gem 'shoulda-matchers'
  gem 'email_spec'
  gem 'launchy'
  gem 'factory_girl'
  gem 'mongoid-rspec', '3.0.0'
end
