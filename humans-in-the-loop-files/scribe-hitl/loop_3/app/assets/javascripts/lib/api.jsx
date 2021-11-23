import JSONAPIClient from 'json-api-client'
import { getCsrfHeaders } from './csrf'

const PATH_TO_API_ROOT = `${window.location.protocol}//${
  window.location.host
}` // 'http://localhost:3000/'

// const PATH_TO_API_ROOT = `${window.location.origin}${window.location.pathname}`

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'application/vnd.api+json; version=1',
  ...getCsrfHeaders()
}

const client = new JSONAPIClient(PATH_TO_API_ROOT, DEFAULT_HEADERS)

export default client
