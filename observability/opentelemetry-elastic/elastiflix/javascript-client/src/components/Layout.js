import React from 'react';
import TmdbLogo from '../tmdb-logo.svg';

const Layout = ({ children }) =>
  <div className='page-container' >
    <div className='content-wrap'>{children}</div>

    <div className="footer">
      Credits: This product uses the TMDB API but is not endorsed or certified by TMDB.
      <div className="footer-logo">
        <img
          className="nav__logo"
          src={TmdbLogo}
          alt=""
        />
      </div>
    </div>
  </div>;


export default Layout;
