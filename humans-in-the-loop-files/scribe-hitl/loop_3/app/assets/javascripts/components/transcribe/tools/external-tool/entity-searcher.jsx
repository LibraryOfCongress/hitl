import React from 'react';

import { BehaviorSubject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

import EntitySelector from './entity-selector.jsx';

export default class EntitySearcher extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      matches: [],
    }
  }

  onSearchText(text) {
    if (this.props.onSearchText) {
      // remove double spaces and spaces at the beginning, don't
      // remove spaces at the end: when people type they should still
      // be able to add spaces
      this.props.onSearchText(text.replace(/  +/g, ' ').replace(/^ /g, ''));
    }
    this.textValue.next(text);
  }

  componentWillMount() {
    this.textValue = new BehaviorSubject('');
    this.textValue.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(textValue => {
      this.setState({ loading: true });
      this.props.searchExternal(textValue, (items) => {
        if (!this.textValue.closed) {
          this.setState({ matches: items });
          this.setState({ loading: false });
        }
      });
    });
  }

  componentWillUnmount() {
    this.textValue.complete()
  }

  componentWillReceiveProps(newProps) {
    this.textValue.next(newProps.searchText || '');
  }

  render() {
    const { searchText } = this.props;
    return <div>
      <input value={searchText}
        onChange={(event) => {
          let text = event.target.value;
          this.onSearchText(text);
        }} />
      {this.state.loading && <p>Searching...</p>}
      <EntitySelector items={this.state.matches}
        getItemValue={(item) => item.display}
        selected={this.props.selected}
        onChange={({ display, id }) => {
          this.props.onChange({ display, id });
        }} />
    </div>
  }
}
