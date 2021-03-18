// Modules to control application life and create native browser window
const {app, BrowserWindow} = require('electron')
const path = require('path')
const childProcess = require('child_process')

var stMosaic
var serverRunning = false
var newLineSent = false
const serverRunningText = "Network URL"

const run_on_win = () => {
  console.log('run on win')
  const run_path = path.join(__dirname, "run", "run.exe")
  //const runtime = childProcess.spawn("powershell.exe", [run_path])
  const runtime = childProcess.spawn(run_path, [], {shell: false})
  console.log('run on win pid', runtime.pid)
  return runtime
}

const run_on_mac = () => {
  console.log('run on mac')
  const runtime = childProcess.spawn(
    "/bin/bash",
    ["-c", "run"],
    {cwd: path.join(__dirname, "run"), detached: true, env: {'LC_ALL': 'en_US.UTF-8'}}
  )
  console.log('run on mac pid', runtime.pid)
  return runtime
}

function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })
 
  if(process.platform == "win32") {
    stMosaic = run_on_win()
  } else {
    stMosaic = run_on_mac()
  }

  stMosaic.stdout.on('data', (data) => {
    console.log("on data:", data.toString())
    console.log("\nindex on data:", data.toString().indexOf(serverRunningText))
    if(!serverRunning && data.toString().indexOf(serverRunningText)) {
      serverRunning = true
      setTimeout(() => {
        mainWindow.loadURL('http://localhost:10000/')
      }, 3000);
    }
    if(!newLineSent) {
      stMosaic.stdin.write('\n')
      console.log('sent newline')
      newLineSent = true
    }
  })
  
  stMosaic.stderr.on('data', (data) => {
    console.error(data.toString())
  })
  
  stMosaic.on('exit', (code) => {
    console.log(`Child exited with code ${code}`)
  })

  mainWindow.loadFile('loading.html')
}

app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('will-quit', function () {
  console.log('app will-quit:', process.platform, stMosaic.pid)
  if(process.platform == "darwin") {
    process.kill(-stMosaic.pid)
  }
})
