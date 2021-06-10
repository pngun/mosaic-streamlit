import path from 'path'
import childProcess from 'child_process'

const electronRoot = path.join(__dirname, "..", "..", "..")
const serverRunningText = "Network URL"
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
        MOSAIC_STREAMLIT_SENTRY_ENABLED: isSentryEnabled
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
        MOSAIC_STREAMLIT_SENTRY_ENABLED: isSentryEnabled
      }
    }
  )
  console.log('run on mac pid', runtime.pid)
  return runtime
}

const run_on_linux = () => {
  const cwd = path.join(__dirname, '../../..')
  console.log('linux cwd', cwd)
  const runtime = childProcess.spawn(
    "/bin/bash",
    ["-c", "./venv-linux/bin/streamlit run src/app.py --server.port=10000"],
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

export default ((targetWindow, sentry_enabled) => {
  let runner
  if (process.platform == "win32") {
    runner = run_on_win(sentry_enabled)
  } else if (process.platform == "darwin") {
    runner = run_on_mac(sentry_enabled)
  } else if (process.platform == "linux") {
    runner = run_on_linux()
  }

  runner.stdout.on('data', (data) => {
    console.log("on data:", data.toString())
    console.log("\nindex on data:", data.toString().indexOf(serverRunningText))
    if(!serverRunning && data.toString().indexOf(serverRunningText)) {
      serverRunning = true
      setTimeout(() => {
        targetWindow.loadURL('http://localhost:10000/')
      }, 3000);
    }
    if(!newLineSent) {
      runner.stdin.write('\n')
      console.log('sent newline')
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
