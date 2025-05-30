import Routes from "./components/Routes";
import { BrowserRouter } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
        {/* <Navigation /> */}
        <Routes />
      </BrowserRouter>
  );
}

export default App;
