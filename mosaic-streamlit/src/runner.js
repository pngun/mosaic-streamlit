import path from 'path'
import childProcess from 'child_process'

export const log = []
const electronRoot = path.join(__dirname, "..", "..", "..")
const networkUrlText = "Network URL: http"
const serverRunningText = "External URL: http"
var serverRunning = false
var newLineSent = false

const run_on_win = (sentry_enabled) => {
  console.log('run on win')
  const isSentryEnabled = sentry_enabled ? 'true' : 'false'
  const run_path = path.join(electronRoot, "runnable", "run.exe")
  const runtime = childProcess.spawn(
    run_path,
    [],
    {
      shell: false,
      env: {
        MOSAIC_STREAMLIT_GUI_RUNNING: 'true',
        MOSAIC_STREAMLIT_SENTRY_ENABLED: isSentryEnabled,
        MOSAIC_STREAMLIT_SEGMENT_ENABLED: 'true'
      }
    }
  )
  console.log('run on win pid', runtime.pid)
  return runtime
}

const run_on_mac = (sentry_enabled) => {
  const isSentryEnabled = sentry_enabled ? 'true' : 'false'
  console.log('run on mac')
  const macRoot = path.join(electronRoot, "runnable", "Contents")
  console.log('mac root', macRoot)

  const runtime = childProcess.spawn(
    "/bin/bash",
    ["-c", "./MacOS/run"],
    {
      cwd: macRoot,
      detached: true,
      env: {
        LC_ALL: 'en_US.UTF-8',
        MOSAIC_STREAMLIT_GUI_RUNNING: 'true',
        MOSAIC_STREAMLIT_SENTRY_ENABLED: isSentryEnabled,
        MOSAIC_STREAMLIT_SEGMENT_ENABLED: 'true'
      }
    }
  )
  console.log('run on mac pid', runtime.pid)
  return runtime
}

const run_on_linux = () => {
  // only for development
  const cwd = path.join(__dirname, '../../..')
  console.log('linux cwd', cwd)
  const runtime = childProcess.spawn(
    "/bin/bash",
    ["-c", "./venv/bin/streamlit run src/app.py --server.port=10000"],
    {
      cwd: cwd,
      detached: true,
      env: {
        LC_ALL: 'en_US.UTF-8',
        MOSAIC_STREAMLIT_GUI_RUNNING: 'true'
      }
    }
  )
  console.log('run on linux pid', runtime.pid)
  return runtime
}

const getPortFromLog = (log) => {
  let port
  const lines = log.join('').split('\n')
  const urlWithPort = lines.filter((line) => {
    return line.indexOf(networkUrlText) >= 0
  })[0].trim()

  const urlIndex = urlWithPort.indexOf(networkUrlText)
  if (urlIndex >= 0) {
    const url = urlWithPort.substring(urlIndex + 20)
    const portIndex = url.indexOf(':')
    if (portIndex) {
      port = url.substring(portIndex + 1).trim()
    }
  }
  return port
}

export default ((targetWindow, sentry_enabled) => {
  var runner
  if (process.platform == "win32") {
    runner = run_on_win(sentry_enabled)
  } else if (process.platform == "darwin") {
    runner = run_on_mac(sentry_enabled)
  } else if (process.platform == "linux") {
    runner = run_on_linux()
  }

  runner.stdout.on('data', (data) => {
    const output = data.toString()
    log.push(output)
    const serverRunningIndex = log.join('').indexOf(serverRunningText)
    if(!serverRunning && serverRunningIndex > -1) {
      runner.port = getPortFromLog(log)
      serverRunning = true
      setTimeout(() => {
        const streamlitUrl = `http://localhost:${runner.port}/` 
        targetWindow.loadURL(streamlitUrl)
      }, 3000);
    }

    if(!newLineSent) {
      runner.stdin.write('\n')
      newLineSent = true
    }
  })

  runner.stderr.on('data', (data) => {
    console.error(data.toString())
  })

  runner.on('exit', (code) => {
    console.log(`Child exited with code ${code}`)
  })
  return runner
})
