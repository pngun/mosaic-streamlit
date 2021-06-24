import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import Logo from './logo.png'

const About = () => {
  return (
    <div className='loader'>
      <img src={Logo} style={{ width: '90%' }} />
      <p>
        <strong>Tapestri Insights v4.0 b1</strong>
      </p>
      <p>
        Copyright (c) 2021 Mission Bio Inc.
      </p>
      <p>
        All rights reserved.
      </p>
    </div>
  )
}

ReactDOM.render(
  <React.StrictMode>
    <About />
  </React.StrictMode>,
  document.getElementById('about-root')
)
