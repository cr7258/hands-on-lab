import React from 'react';

const title:string = "React 表达式";

const n1:number = 1;
const n2:number = 2;

const userinfo = {
  name: "king",
  age: 26,
  gender: true
};

function getUserInfo(ui:any) {
  return `${ui.name} is a ${ui.gender ? "boy": "girl"} and ${ui.age} years old.`
}

const arrParagraph = [
  <p>Name: king</p>,
  <p>Age: 26</p>,
  <p>Gender: boy</p>
]

const smallSize = {
  fontSize: 12
}

const mediumSize = {
  fontSize: 16
}

const largeSize = {
  fontSize: 20
}

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* React Expression */}
        <p>{title}</p>
        <p style={smallSize}>{n1} + {n2} = {n1 + n2}</p>
        <p style={mediumSize}>{userinfo.name} is a {userinfo.gender ? "boy" : "girl"} and {userinfo.age} years old.</p>
        <p style={largeSize}>{getUserInfo(userinfo)}</p>
        <p>{arrParagraph}</p>
      </header>
    </div>
  )
}

export default App;
