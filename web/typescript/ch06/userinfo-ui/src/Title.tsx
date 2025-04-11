import React, { Component } from 'react';

interface IProps {
    title? : string;
}

interface IState {}
    
export default class Title extends Component<IProps, IState> {
    private static defaultProps = {
        title: "Default Information"
    };

    render() {
        return (
            <h3>{this.props.title}</h3>
        );
    }
}