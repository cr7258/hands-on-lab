import React from 'react';
import Intro from './Intro';
import Title from './Title';
import Info from './Info';
import Footer from './Footer';
import './App.css';

const title = <Title />;
const cIntro = {
  avatar: "avatar01.png",
  alt: "loading...",
  nickname: "Super King",
};

const intro = <Intro avatar={cIntro.avatar} alt={cIntro.alt} nickname={cIntro.nickname} />;

const cInfo = {
  uid: "007",
  uname: "King James",
  gender: true,
  age: 26,
  email: "king@example.com",
};

const info = <Info uid={cInfo.uid} uname={cInfo.uname} gender={cInfo.gender} age={cInfo.age} email={cInfo.email} />;

const footer = <Footer date={new Date()} />;

function App() {
  return (
    <div className="App">
      <div className="container">
        <div className="header">
          {title}
        </div>
        <div className="content">
          <div className="sidebar">
            {intro}
          </div>
          <div className="main-content">
            {info}
          </div>
        </div>
        <div className="footer">
          {footer}
        </div>
      </div>
    </div>
  );
}

export default App;