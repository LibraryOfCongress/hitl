import React from "react";

export default class EntitySelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = { selected: props.selected || 'unknown' };
  }

  componentWillReceiveProps(newProps) {
    let selected = newProps.selected || this.state.selected;
    let items = newProps.items || this.state.items;

    // check that the selection is still valid
    if (items && selected != 'unknown') {
      for (let item of items) {
        if (item.id == selected) {
          return;
        }
      }

      this.setSelected('unknown');
    }
  }

  setSelected(item) {
    if (item == 'unknown') {
      item = { id: 'unknown', display: 'Unknown entity' };
    }
    this.props.onChange(item);
    this.setState({ selected: item.id });
  }

  render() {
    function renderItem(self, item) {
      return <label className="radio" key={item.id}>
        <input type="radio" value={item.id}
          checked={self.state.selected === item.id}
          onChange={() => self.setSelected(item)} />
        {item.display}
      </label>
    }

    return this.props.items.length && <div>
      <p>Select if this matches any of the results in the list:</p>
      <div className="entity-list">
        {
          this.props.items.map((item) => renderItem(this, item))
        }
        {renderItem(this, { id: 'unknown', display: 'Unknown / Other' })}
      </div>
    </div> || <span>No results!</span>
  }
}
