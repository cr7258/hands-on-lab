import React, { Component } from 'react';
import Fab from './Fab';


interface IProps {
  pFab: string
}

interface IState {
  n0: number,
  n1: number,
  sFab: string
}

class FabComp extends Component<IProps, IState> {
  constructor(props: IProps) {
    super(props);
    this.state = {
      n0: 0,
      n1: 1,
      sFab: this.props.pFab
    };
  }

  // componentDidMount() {
  //   console.log('App: Component DID MOUNT');
  // }

  // componentDidUpdate(prevProps: IProps, prevState: IState) {
  //   console.log('App: Component DID UPDATE');
  //   if(prevState.sFab !== this.state.sFab) {
  //     console.log("PrevProps.pFab: " + prevProps.pFab);
  //     console.log("this.props.pFab: " + this.props.pFab);
  //     console.log("this.state.sFab: " + this.state.sFab);
  //   }
  // }

  render() {
    return (
      <div>
        <h3>Fibonacci Sequence</h3>
        <Fab fab={this.state.sFab} />
        <button className="btn" onClick={this.btnClickFab.bind(this)}>Generate Fibonacci Sequence</button>
      </div>
    );
  }

  btnClickFab() {
    let na: number = this.state.n1;
    let nb: number = this.state.n0 + this.state.n1;
    let strFab = this.state.sFab

    this.setState({
      n0: na,
      n1: nb,
      sFab: strFab + " " + nb.toString()
    });
    console.log("this.props.pFab: " + this.props.pFab);
  }
}

// 创建了一个 FabComp 组件的实例，并传递了一个名为 pFab 的属性，其值为字符串"0 1"
const cFabComp = <FabComp pFab="0 1" />;

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {cFabComp}
      </header>
    </div>
  );
}

export default App;
