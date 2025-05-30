import * as React from "react";
import ComingSoon from '../coming-soon.png'

function Card(props) {
  const renderCast = !!props.movie.cast.raw.length && <div className="cast"><p>Starring {props.movie.cast.raw.slice(0, 4).map(c => c + ", ")} ... </p></div>

  return (
    <div 
      className="card"
      onClick={() => {
        window.localStorage.setItem('movie', JSON.stringify({
            title: props.movie.title.raw,
            description: props.movie.overview.raw,
            backdrop: `https://image.tmdb.org/t/p/original/${props.movie.poster_path.raw}`,
            id: props.movie.id.raw
        }))
        window.location.href = "/home"
    }}  
    >
      <div className="wrapper">
        <div className="image">
          <div className="poster">

            <img loading="lazy" className="poster" src={!props.movie.poster_path.raw ? ComingSoon : `https://image.tmdb.org/t/p/original/${props.movie.poster_path.raw}`} alt={props.movie.title.raw} />
          </div>
        </div>
        <div className="details">
          <div className="wrapper">
            <div className="title">
              <div>
                <h2 dangerouslySetInnerHTML={{__html: props.movie.title.raw}} />
              </div>
              <span className="release_date">
                {Date(props.movie.release_date.raw) > new Date() ? 'Releasing ' : 'Released '}
                {new Intl.DateTimeFormat("en-GB", {
                  year: "numeric",
                  month: "long",
                  day: "2-digit"
                }).format(new Date(props.movie.release_date.raw))}</span>
            </div>
          </div>
          <div className="overview">
            <p dangerouslySetInnerHTML={{ __html: props.movie.overview.raw}} />
          </div>
          {renderCast}
        </div>
      </div>
    </div>
  )

}

export default Card
