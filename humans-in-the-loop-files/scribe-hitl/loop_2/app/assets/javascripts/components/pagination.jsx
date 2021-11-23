import React from 'react'

export default class Pagination extends React.Component {
  static defaultProps = {
    max_links: 12
  }

  pageUrl = (page) => {
    const base = location.href.replace(/(&|\?)page=[^&]+/, '')
    return `${base}${base.indexOf('?') >= 0 ? '&' : '?'}page=${page}`
  }

  render = () => {
    // Build array of page numbers to show..    
    let pages = []
    if (this.props.total_pages <= this.props.max_links) {
      // If fewer pages than max, show them all:
      pages = Array.from({ length: this.props.total_pages }, (_, k) => k + 1)
    }
    else {
      // Too many to show, so truncate..
      // Assuming we want three groups of truncated links (first few, last few,
      // and a middle group centered around current page)..
      const chunk_size = this.props.max_links / 3 - 1
      for (let p = 1; p <= this.props.total_pages; p++) {
        // Add first few pages:
        if (p <= chunk_size) pages.push(p)
        // Add a middle group of pages around the current page:
        if (Math.abs(this.props.current_page - p) <= chunk_size / 2 && pages.indexOf(p) < 0) pages.push(p)
        // Bookend with last few pages:
        if (p > this.props.total_pages - chunk_size && pages.indexOf(p) < 0) pages.push(p)
      }
    }
    // Don't show anything if no usable links:
    if (pages.length < 2) return null

    const page_links = []

    // Add leading < link
    if (this.props.prev_page) page_links.push({ label: '&lt;', page: this.props.prev_page, title: 'Previous', disabled: false })

    for (let i in pages) {
      const page = pages[i]
      // Add divider if this page is the beginning of a chunk:
      if (i > 0 && pages[i - 1] != page - 1) page_links.push({ dotdotdot: true })
      // Add page link:
      page_links.push({ label: page, page: page, title: `Page ${page}`, disabled: page == this.props.current_page })
    }

    // Add final > link
    if (this.props.next_page) page_links.push({ label: '&gt;', page: this.props.next_page, title: 'Next', disabled: false })

    return <ul className="pagination">
      {page_links.map((link, i) => {
        if (link.dotdotdot)
          return <li key={i} className="divider" />
        else if (link.disabled)
          return <li key={i} className="disabled"><span dangerouslySetInnerHTML={{ __html: link.label }} /></li>
        else
          return <li key={i}><a href={this.pageUrl(link.page)} title={link.title} dangerouslySetInnerHTML={{ __html: link.label }} /></li>
      })
      }
    </ul>
  }
}