import React, { Component } from 'react';

interface IProps {
    avatar: string;
    alt: string;
    nickname: string;
}

interface IState {}

export default class Intro extends Component<IProps, IState> {
    render() {
        return (
            <div>
                <img className="" src={this.props.avatar} alt={this.props.alt} />
                <p className="Nickname">{this.props.nickname}</p>
            </div>
        );
    }
}
