/*
 * decaffeinate suggestions:
 * DS101: Remove unnecessary use of Array.from
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React from 'react'
import ReactDOM from 'react-dom'
import createReactClass from 'create-react-class'
import qs from 'query-string'
import { getCsrfHeaders } from '../lib/csrf'

const NameSearch = createReactClass({
  displayName: 'NameSearch',

  // fieldKey: ->
  //   if @props.standalone
  //     'value'
  //   else
  //     @props.annotation_key

  handleKeyPress(e) {
    const term = e.target.value
    const el = $(ReactDOM.findDOMNode(this))
    return el.autocomplete({
      source: (request, response) => {
        return $.ajax({
          url: `/subject_sets/terms/${this.props.field}`,
          dataType: 'json',
          data: {
            q: request.term
          },
          headers: getCsrfHeaders(),
          success: data => {
            let unit
            const names = []
            if (data.length !== 0) {
              for (let n of Array.from(data)) {
                unit = {}
                unit['label'] = n.meta_data.name
                unit['value'] = n
                names.push(unit)
              }
            } else {
              unit = {}
              unit['label'] =
                'Currently, there is no match. Please check back in a few days.'
              names.push(unit)
            }
            return response(names)
          },
          error: (xhr, thrownError) => {
            return console.log(xhr.status, thrownError)
          }
        })
      },
      focus: (e, ui) => {
        return e.preventDefault()
      },

      select: (e, ui) => {
        e.target.value
        this.context.router.history.push(
          '/mark?' + qs.stringify({ subject_set_id: ui.item.value.id })
        )
      }
    })
  },

  render() {
    return (
      <input id="name-search" type="text" placeholder="Search Records by Name" onKeyDown={this.handleKeyPress} />
    )
  }
})

export default NameSearch
