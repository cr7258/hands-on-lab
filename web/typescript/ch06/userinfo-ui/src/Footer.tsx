import React, { Component } from 'react';

interface IProps {
    date: Date;
}

interface IState {}

export default class Footer extends Component<IProps, IState> {
    render() {
        return (
            <p className="footer">Super React Co. {formatDate(this.props.date)}</p>
        );
    }
}

function formatDate(date: Date) {
    return date.toLocaleDateString();
}
