import React, { useState, useEffect, useCallback } from 'react';
import { apm } from '../App';

// set to  if testing locally with npm
const endpoint =  process.env.NODE_ENV === 'development' ?  process.env.REACT_APP_NODE_BACKEND_HOST : "${NODE_BACKEND_HOST}"

console.log("endpoint: " + endpoint)

// initialise favorites using state

function addTofavorites(movie, favorites, setfavorites, setIsLoading, setLastRequestSuccessful) {
  setIsLoading(true);
  // sleep for 1 second

  fetch(endpoint + '/api/favorites', {
    method: 'POST',
    mode: "cors",
    headers: {
      'Content-Type': 'application/json'
    },
    
    body: JSON.stringify(movie)
  })
  .then(res => res.json())
  .then(data => {
    console.log(data.favorites)
    console.log(movie.id)
    console.log(data)
    if (data.error != null) {
      setLastRequestSuccessful(false);
      console.log("failed to update favorites")
      const transaction = apm.startTransaction('custom managed', 'custom', { managed: true })
      apm.captureError(new Error("failed to update favorites"))
      transaction.end()
    } else {
      setfavorites(data.favorites)
      setLastRequestSuccessful(true);
    }
    setIsLoading(false);
  }).catch(error => {
    setIsLoading(false);
    setLastRequestSuccessful(false);
    console.log(error)
    const transaction = apm.startTransaction('custom managed', 'custom', { managed: true })
    apm.captureError(error)
    transaction.end()
  }
  )
}


function Header({ movie, setMovie }) {
  const [favorites, setfavorites] = useState([])
  const [buttonText, setButtonText] = useState();
  const [isLoading, setIsLoading] = useState(false);
  // track if last request to favorites was successful
  const [lastRequestSuccessful, setLastRequestSuccessful] = useState(true);

  // if favoriteslist includes the current movie, change the button text to remove from favorites
  useEffect(() => {
    fetch(endpoint + '/api/favorites', {
      method: 'GET',
      mode: "cors",
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(res => res.json())
    .then(data => {
      console.log(data)
      if (data.error != null) {
        setLastRequestSuccessful(false);
      } else {
        setLastRequestSuccessful(true);
      }
      setfavorites(data.favorites)
    })
    
  }, [])

  useEffect(() => {
    console.log(favorites.favorites)
    console.log(movie.id)
    if (favorites.favorites?.includes(String(movie.id))) {
      setButtonText("Remove from favorites")
    } else {
      setButtonText("Add to favorites")
    }
  }, [favorites, movie.id])

  return (
    <header className="banner" style={{
      backgroundSize: "cover",
      backgroundImage: `url("${movie.backdrop}")`,
      backgroundPosition: "center center"
    }}>
      <div className="banner__contents">
        <h1 className="banner__title">{ movie.title } </h1>
        <div className="banner__buttons">
          <button className="banner__button" disabled style={{ opacity: 0.5, cursor: 'not-allowed'}}>Play</button>
          {
            isLoading ? (
              <button 
                className="banner__button"
                // onclick add the current movie to the favorites
                name='favorites'
                // disable button while loading
                disabled={true}
                style={{ backgroundColor: lastRequestSuccessful ? '' : '#CC4444' }}
              >
                Loading...
              </button>
            ) : (
              <button 
                className="banner__button"
                // onclick add the current movie to the favorites
                name='favorites'
                onClick={() => {
                  addTofavorites(movie, favorites, setfavorites, setIsLoading, setLastRequestSuccessful)
                }}
                // set backgroundcolor of button to red if it is in favorites
                style={{ backgroundColor: lastRequestSuccessful ? '' : '#CC4444' }}
              >
                {buttonText}
              </button>
            )
          }
          {
            lastRequestSuccessful ? (
              <></>
            ) : (
                <button 
                  className="banner__button"
                  // onclick add the current movie to the favorites
                  name='favorites'
                  onClick={() => {
                    addTofavorites(movie, favorites, setfavorites, setIsLoading, setLastRequestSuccessful)
                  }}
                  // set backgroundcolor of button to red if it is in favorites
                  style={{ backgroundColor: lastRequestSuccessful ? '' : '#CC4444', cursor: 'help' }}
                  disabled={true}
                >
                  {"Error: Failed to update favorites, please try again later"}
                  
                </button>
            )
          }
        </div>
        <p className="banner__description">{ movie.description }</p>
      </div>
      <div className="banner--fadeBottom"></div>
    </header>
  );
}

export default Header;
