require 'net/http'
require 'json'
require 'uri'

class ExternalsController < ApplicationController
  respond_to :json

  def search
    externals = Project.current.externals
    external = externals.select{ |item| item[:id] == params[:id] }.first()

    filled_uri = ''
    last_index = 0

    # replace all the placeholders in the uri from the project definition
    base_uri = external[:uri]
    loop do
      match = base_uri.match(/\{((?<env>env:)|)(?<key>[^\}]+)\}/, last_index)
      break if match.nil?
      
      filled_uri << base_uri[last_index..match.begin(0)-1]
      last_index = match.end(0)
      # TODO: escape?
      if match[:env].nil?
        filled_uri << URI.escape(params[match[:key]])
      else
        filled_uri << URI.escape(ENV[match[:key]])
      end
    end
    filled_uri << base_uri[last_index..-1]

    response = Net::HTTP.get(URI(filled_uri))

    mapped = JSON.parse(response).map { |item|
      {
        "id" => item[external[:id_field]],
        "display" => item[external[:display_field]],
      }
    }

    render json: mapped
  end

end
