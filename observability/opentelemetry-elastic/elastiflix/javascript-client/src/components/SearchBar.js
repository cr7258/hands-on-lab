import React from 'react';
import {
    SearchBox,
} from '@elastic/react-search-ui';
import { EuiIcon } from '@elastic/eui';
import { useHistory } from "react-router-dom";


import AppSearchAPIConnector from "@elastic/search-ui-app-search-connector";
import { SearchProvider } from "@elastic/react-search-ui";


const renderInput = ({ getAutocomplete, getInputProps, getButtonProps }) => {
    return (
        <div className="search-box">
            <EuiIcon className="search-box__icon" type="search" />
            <input
                {...getInputProps({
                    className: "search-box__input",
                    placeholder: "Search by title, cast name..."
                })}
            />
            {getAutocomplete()}
        </div>
    )
}

function SearchBar() {

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

    // const connector = new AppSearchAPIConnector({
    //     searchKey: process.env.REACT_APP_AS_SEARCH_API_KEY,
    //     engineName: process.env.REACT_APP_ENGINE_NAME,
    //     endpointBase: process.env.REACT_APP_AS_BASE_URL,
    //     cacheResponses: false
    // });

    const configurationOptions = {
        initialState: { sortDirection: "desc", sortField: "popularity", resultsPerPage: 15 },
        apiConnector: connector,
        trackUrlState: false,
        alwaysSearchOnInitialLoad: false,
        autocompleteQuery: {
            results: {
                result_fields: {
                    title: {
                        snippet: {
                            size: 100
                        }
                    }
                }
            },
            suggestions: {
                types: {
                  // Limit query to only suggest based on "title" field
                  documents: { fields: ["title.completion"] }
                }
            }
        },
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
              }
            }
          },
    };

    

    const history = useHistory();

    return (
        <SearchProvider config={configurationOptions}>
            <SearchBox
                searchAsYouType={true}
                inputView={renderInput}
                autocompleteSuggestions={{
                    sectionTitle: "Suggested Queries"
                }}
                autocompleteMinimumCharacters={2}
                onSubmit={searchTerm => {
                    history.push("/search?q=" + searchTerm);
                }}
                onSelectAutocomplete={(selection, defaultOnSelectAutocomplete) => {
                    if (selection.suggestion) {
                        history.push("/search?q=" + selection.suggestion);
                    } else {
                        defaultOnSelectAutocomplete(selection);
                    }
                }}
            /> 
            {/* <SearchBox 
                searchAsYouType={false}
                inputView={renderInput}
                autocompleteResults={{
                titleField: "title",
                urlField: "backdrop_path",
                }} 
                onSubmit={searchTerm => {
                    history.push("/search?q=" + searchTerm);
                }}
                onSelectAutocomplete={(selection, defaultOnSelectAutocomplete) => {
                    if (selection.title) {
                        history.push("/search?q=" + selection.title.raw);
                    } else {
                        defaultOnSelectAutocomplete(selection);
                    }
                }}
                />; */}
        </SearchProvider>
    );
}

export default SearchBar;