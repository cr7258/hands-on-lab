import React, { Component } from 'react';

interface IProps{}
interface IState{
  date: Date;
  timerId: NodeJS.Timer,
}

class StateClock extends Component<IProps, IState> {
  constructor(props: IProps) {
    super(props);
  }

  state = {
    date: new Date(),
    timerId: setInterval(() => {}),
  }

  componentDidMount() {
    this.setState({
      timerId: setInterval(() => this.tick(), 1000),
    });
  }

  componentWillUnmount() {
    clearInterval(this.state.timerId);
  }

  tick() {
    this.setState({
      date: new Date(),
    });
  }

  render() {
    return (
      <div>
        <h3>React States - State Clock App</h3>
        <p>Now is {this.state.date.toLocaleTimeString()}.</p>
      </div>
    );
  }
}

const cStateClock = <StateClock />;

function App() {
  return (
    <div className="App">
      {cStateClock}
    </div>
  );
}
  
export default App;
