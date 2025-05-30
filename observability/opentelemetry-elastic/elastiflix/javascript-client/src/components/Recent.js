import AppSearchAPIConnector from "@elastic/search-ui-app-search-connector";
import { SearchProvider, WithSearch } from "@elastic/react-search-ui";

import ComingSoon from '../coming-soon.png'

function Recent({ movie, setMovie }) {
  class CustomConnector {
    constructor(host) {
      this.host = host;
    }
  
    async onSearch(query, options) {
      const response = await fetch(this.host + "/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query,
          options
        })
      });
      return response.json();
    }
  
    async onAutocomplete(query, options) {
      const response = await fetch(this.host + "/autocomplete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query,
          options
        })
      });
      return response.json();
    }
  }
  
const endpoint =  process.env.NODE_ENV === 'development' ?  process.env.REACT_APP_NODE_BACKEND_HOST : "${NODE_BACKEND_HOST}"
const connector = new CustomConnector(endpoint);
const config = {
    debug: true,
    initialState: { sortDirection: "asc", sortField: "release_date", resultsPerPage: 10 },
    searchQuery: {
      search_fields: {
        title: {
          weight: 3
        }
      },
      result_fields: {
        title: {
          snippet: {}
        },
        poster_path: {
          snippet: {}
        },
        backdrop_path: {
            snippet: {}
          },
        overview: {
          snippet: {}
        },
        release_date: {
            snippet: {}
          },
        id: {
          snippet: {}
        },
        "workaround-recent": {
          snippet: {}
        }
      }
    },
    apiConnector: connector,
    alwaysSearchOnInitialLoad: true,
    trackUrlState: false
  };

  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ searchTerm, setSearchTerm, results }) => ({ searchTerm, setSearchTerm, results })}>
        {({ searchTerm, setSearchTerm, results }) => (
          <div className="row">
            <h2>Recent movies</h2>
            <div className="row__posters">
              {

              results.filter(r => r.poster_path.raw !== null).map(r =>
                
                <img
                  key={r.id.raw}
                  className="row__poster row__posterLarge"
                  src={!r.poster_path.raw ? ComingSoon : `https://image.tmdb.org/t/p/original/${r.poster_path.raw}`}
                  alt={r.title.raw}
                  onClick={() => {
                    console.log(r)
                    setMovie({
                      title: r.title.raw,
                      description: r.overview.raw,
                      backdrop: `https://image.tmdb.org/t/p/original/${r.backdrop_path.raw}`,
                      id: r.id.raw
                  })
                }}
                />
              )}
            </div>
          </div>
        )}
      </WithSearch>
    </SearchProvider>
  );
}

export default Recent;
