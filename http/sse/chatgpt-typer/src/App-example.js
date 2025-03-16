import React from "react";
import { TypeAnimation } from "react-type-animation";

const ExampleComponent = () => {
  return (
    <TypeAnimation
      style={{ whiteSpace: "pre-line", height: "195px", display: "block" }}
      sequence={[
        `Line one\nLine Two\nLine Three\nLine Four\nLine Five
      
  Line Seven`, // actual line-break inside string literal also gets animated in new line, but ensure there are no leading spaces
        1000,
        "",
      ]}
      repeat={Infinity}
    />
  );
};

function App() {
  return (
    <div style={{ padding: "20px" }}>
      <ExampleComponent />
    </div>
  );
}

export default App;
