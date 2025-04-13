import React, { Component } from 'react';

type IProps = {
  fab: string
}

type IState = {
}

export default class Fab extends Component<IProps, IState> {
    // state = {}
    // componentWillReceiveProps(newProps: IProps) {
    //     console.log('Fab: Component will receive props');
    //     if(newProps.fab !== this.props.fab) {
    //         console.log("newProbs.fab: " + newProps.fab);
    //         console.log("this.props.fab: " + this.props.fab);
    //     }
    // }

    render() {
        return (
            <p>{this.props.fab}</p>
        );
    }
}