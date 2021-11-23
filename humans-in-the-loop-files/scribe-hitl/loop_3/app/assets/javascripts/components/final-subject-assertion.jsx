import React from 'react'
import PropTypes from 'prop-types'

export default class FinalSubjectAssertion extends React.Component {
  static propTypes = {
    assertion: PropTypes.object.isRequired
  }

  constructor(props) {
    super(props)
    this.state = {
      showingRegion: false
    }
  }

  toggleRegion = () => {
    console.log('show: ', !this.state.showingRegion)
    this.setState({ showingRegion: !this.state.showingRegion })
  }
  render = () => {

    const confidence = Math.round(100 * this.props.assertion.confidence)
    let confidence_label = 'low'
    if (confidence >= 50)
      confidence_label = 'med'
    if (confidence >= 66)
      confidence_label = 'high'
    if (confidence == 100)
      confidence_label = 'max'

    const status_label = this.props.assertion.status.replace(/_/, ' ')

    return (
      <div className={`confidence-${confidence_label} status-${this.props.assertion.status}`}>
        <h3>{this.props.assertion.name}</h3>

        <ul className="assertion-data">
          {this.props.assertion.data.map((k) => {
            let cleaned_version = null
            if (this.props.field && this.props.field.value)
              cleaned_version = (typeof this.props.field.value) == 'object' ? this.props.field.value[k] : this.props.field.value

            return (<li key={k}>
              <span className="value">{this.props.assertion.data[k]}</span>
              {cleaned_version && ('' + cleaned_version) != this.props.assertion.data[k] &&
                <span className="cleaned-version">( Interpreted as <em>{(typeof cleaned_version) == 'object' ? cleaned_version.join(' x ') : cleaned_version}</em> )</span>
              }
              {k != 'value' &&
                <span className="data-key">({k.replace(/_/g, ' ')})</span>
              }
            </li>)
          })}
        </ul>
        <dl className="assertion-properties">
          <dt className="confidence">Confidence</dt>
          <dd className="confidence">{confidence}%</dd>
          <dt className="status">Status</dt>
          <dd className="status">{status_label}</dd>
          <dt>Distinct Transcriptions</dt>
          <dd>{this.props.assertion.versions && this.props.assertion.versions.length || 0}</dd>
        </dl>
        <a className="show-region-link" href="javascript:void(0);" onClick={this.toggleRegion}>
          {this.state.showingRegion ?
            <span>Hide {this.props.project.term('mark')}</span> :
            <span>Show {this.props.project.term('mark')}</span>
          }
        </a>
        {
          (() => {
            const viewer_width = this.props.assertion.region.width,
              scale = viewer_width / this.props.assertion.region.width,
              s = {
                background: `url(${this.props.subject.location.standard}) no-repeat -${Math.round(this.props.assertion.region.x * scale)}px -${Math.round(this.props.assertion.region.y * scale)}px`,
                width: viewer_width + 'px',
                height: (this.state.showingRegion ? Math.round(this.props.assertion.region.height * scale) : 0) + 'px'
              },
              classes = ['image-crop']
            if (this.state.showingRegion) {
              classes.push('showing')
            }
            return <div className={classes.join(' ')} src={this.props.subject.location.standard} style={s} />
          })()
        }
      </div>)
  }
}
