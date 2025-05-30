import Nav from "./Nav";
import Header from "./Header";

import Popular from "./Popular";
import Recent from "./Recent";

import { useState } from "react";

function Home() {
    const [movie, setMovie] = useState({
        title: "Luca",
        description: "Luca and his best friend Alberto experience an unforgettable summer on the Italian Riviera. But all the fun is threatened by a deeply-held secret: they are sea monsters...",
        backdrop: "https://image.tmdb.org/t/p/original/jTswp6KyDYKtvC52GbHagrZbGvD.jpg",
        id: 508943
      })

    return (
        <div className="app">
            <Nav showSearch={true} fixed={true}/>
            <Header movie={movie} setMovie={setMovie}/>
            <div className="recommendations">
                <Popular movie={movie} setMovie={setMovie}/>
                <Recent movie={movie} setMovie={setMovie}/>
            </div>
        </div>
    )
}

export default Home
