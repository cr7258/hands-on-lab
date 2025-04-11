import React, { Component } from 'react';

interface IProps {
    uid: string,
    uname: string,
    gender: boolean,
    age: number,
    email: string,
}

interface IState {}

export default class Info extends Component<IProps, IState> {
    render() {
        return (
            <div>
                <p className="info-small">id: {this.props.uid}</p>
                <p className="info-middle">name: {this.props.uname}</p>
                <p className="info-middle">gender: {this.props.gender ? "boy" : "girl"}</p>
                <p className="info-middle">age: {this.props.age}</p>
                <p className="info-small">email: {this.props.email}</p>
            </div>
        );
    }
}
