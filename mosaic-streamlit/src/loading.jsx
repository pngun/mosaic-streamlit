import * as React from 'react';
import * as ReactDOM from 'react-dom';
import loadingGif from './static/loader.gif'

const Loading = () => (
  <div className='loader'>
    Starting the Streamlit server
    <br /><br /><br />
    <img className='spinner' src={loadingGif} />
  </div>
)

ReactDOM.render(<Loading />, document.getElementById('loading'));
