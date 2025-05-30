import React, { useState, useEffect } from 'react';
import SearchBar from "./SearchBar";
import logo from '../logo.svg'

function Nav(props) {

    // set to  if testing locally with npm
    //const endpoint = "";
    const endpoint =  process.env.NODE_ENV === 'development' ?  process.env.REACT_APP_NODE_BACKEND_HOST : "${NODE_BACKEND_HOST}"

    const [username, setUsername] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(endpoint + '/api/login') // replace with your .NET service URL
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Something went wrong ...');
                }
            })
            .then(data => {
                setUsername(data.userName);
                setIsLoading(false);
            })
            .catch(error => {
                setIsLoading(false);
                setError(error);
            }); 
            
    }, []);

    if (isLoading) {
        return <div>Loading ...</div>
    }

    if (error) {
        return <div>Error: {error.message}</div>
    }

    return (
        <div className={`nav ${props.fixed? "nav-fixed" : ""}`} >
            <a href="/">
                <img
                    className="nav__logo"
                    src={logo}
                    alt=""
                />
            </a>
            <div className="nav__right">
                <div className="nav__user">
                    <div className="nav__user__name">
                        <h3></h3>
                    </div>
                </div>
            </div>
            <div>
                <div className="username">User: {username}</div>
                {props.showSearch ? <div className="search_bar">
                    <SearchBar /> 
                </div> : <></>}
            </div>
        </div>
    );
}

// Set default props
Nav.defaultProps = {
    showSearch: false,
    fixed: false
};

export default Nav;
