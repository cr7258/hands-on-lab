import Routes from "./components/Routes";
import { BrowserRouter } from "react-router-dom";
import { init as initApm } from '@elastic/apm-rum'

export const apm = initApm({
  serviceName: process.env.NODE_ENV === 'development' ?  "javascript-client-elastic-manual" : "${ELASTIC_APM_SERVICE_NAME}",
  //serverUrl: 'https://fef53b05d7d8455699151da2edc8f280.apm.us-central1.gcp.cloud.es.io:443',
  serverUrl: process.env.NODE_ENV === 'development' ?  process.env.REACT_APP_ELASTIC_APM_SERVER_URL : "${ELASTIC_APM_SERVER_URL}",
  serviceVersion: '',
  environment: process.env.NODE_ENV === 'development' ?  "dev" : "${ELASTIC_APM_ENVIRONMENT}",
  distributedTracingOrigins: ['http://localhost:3000','http://localhost:3001','http://localhost:9000']
})

function App() {
  return (
    <BrowserRouter>
        {/* <Navigation /> */}
        <Routes />
      </BrowserRouter>
  );
}

export default App;
