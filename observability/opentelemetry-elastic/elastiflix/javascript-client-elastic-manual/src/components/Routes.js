import React from 'react';
import { Route, Switch, Redirect } from "react-router-dom";
import SearchPage from './SearchPage';
import Home from './Home.js';
import Layout from './Layout.js';


const Routes = () => (
    <>
        <Switch>
          <RouteWrapper exact path="/">
            <Redirect to="/home" />
          </RouteWrapper>
          <RouteWrapper exact path="/home" component={Home} layout={Layout}/>
          <RouteWrapper exact path="/search" component={SearchPage} layout={Layout}/>
        </Switch>
    </>
)

function RouteWrapper({
  component: Component, 
  layout: Layout, 
  ...rest
}) {
  return (
    <Route {...rest} render={(props) =>
      <Layout {...props}>
        <Component {...props} />
      </Layout>
    } />
  );
}

export default Routes;