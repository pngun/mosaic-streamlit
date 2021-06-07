import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

const useInput = () => {
  const [value, setValue] = useState('')
  useEffect(() => {
    async function isSentryEnabled() {
      const sentryValue = await window._app.isSentryEnabled()
      console.log('sentryValue', sentryValue, window._app)
      setValue(sentryValue)
    }
    isSentryEnabled()
  }, [])
  const onChange = (enabled) => {
    setValue(enabled)
    window._app.setSentry(enabled)
  }
  const input = <input checked={value} onChange={e => onChange(event.target.checked)} type='checkbox' />
  return [value, input]
}

const Settings = () => {
  const [value, Input] = useInput()

  return (
    <div className='loader'>
      <h1>
        Settings
      </h1>
      <p>
        <strong>Allow error tracking</strong>
        <br />
        This enables the application to send technical errors to the Sentry application errors server.
        <br />
        <br />

        {Input}&nbsp;Allow sending technical errors to the remote server
      </p>
    </div>
  )
}

ReactDOM.render(
  <React.StrictMode>
    <Settings />
  </React.StrictMode>,
  document.getElementById('settings-root')
)
