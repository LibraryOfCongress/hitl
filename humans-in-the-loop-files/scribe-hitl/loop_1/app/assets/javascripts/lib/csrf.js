export function getCsrfHeaders() {
  return {
    'X-CSRF-Token': $('meta[name=csrf-token]').attr('content')
  }
}
