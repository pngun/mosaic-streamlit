const {
  app, ipcMain, webContents, globalShortcut, Menu, MenuItem, BrowserWindow
} = require('electron')

if(require('electron-squirrel-startup')) app.quit()

const path = require('path')
const childProcess = require('child_process')

var mainWindow
var aboutWindow
var stMosaic
var serverRunning = false
var newLineSent = false
const serverRunningText = "Network URL"

const run_on_win = () => {
  console.log('run on win')
  const run_path = path.join(__dirname, "run", "run.exe")
  //const runtime = childProcess.spawn("powershell.exe", [run_path])
  const runtime = childProcess.spawn(
    run_path,
    [],
    {
      shell: false,
      env: { MOSAIC_STREAMLIT_GUI_RUNNING: 'true' }
    }
  )
  console.log('run on win pid', runtime.pid)
  return runtime
}

const run_on_mac = () => {
  console.log('run on mac')
  const runtime = childProcess.spawn(
    "/bin/bash",
    ["-c", "./MacOS/run"],
    {
      cwd: path.join(__dirname, "run.app", "Contents"),
      detached: true,
      env: {
        LC_ALL: 'en_US.UTF-8',
        MOSAIC_STREAMLIT_GUI_RUNNING: 'true'
      }
    }
  )
  console.log('run on mac pid', runtime.pid)
  return runtime
}

const about = (parent) => {
  const windowOptions = process.platform == "win32" ? {
    modal: true,
  } : {
    frame: false,
    titleBarStyle: 'hiddenInset',
  }
  aboutWindow = new BrowserWindow({
    parent: parent,
    show: false,
    width: 400,
    height: 400,
    ...windowOptions
  })
  aboutWindow.loadFile('release.html')
  aboutWindow.removeMenu()
  aboutWindow.once('ready-to-show', () => {
    aboutWindow.setClosable(true)
    aboutWindow.show()
  })
}

function createWindow () {
  mainWindow = new BrowserWindow({
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

function createAnotherWindow () {
  const anotherWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })
  anotherWindow.loadURL('http://localhost:10000/')
}

app.whenReady().then(() => {
  const template = [
    { label: 'Application', submenu: [
      { label: 'New Window', click: () => { createAnotherWindow() } },
      {
        label: 'Search',
        accelerator: 'CmdOrCtrl+F',
        click() {
          mainWindow.webContents.send('toggle-find')
        }
      },
      { label: 'About', click: () => { about(mainWindow) } },
      { label: 'Quit', role: 'quit' },
    ]},
    { role: 'editMenu' },
  ]
  menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)

  createWindow()

  ipcMain.on('find-text', (event, text) => {
    mainWindow.webContents.findInPage(text)
  })
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('will-quit', function () {
  console.log('app will-quit:', process.platform, stMosaic.pid)
  if(process.platform != "win32") {
    process.kill(-stMosaic.pid)
  }
})
