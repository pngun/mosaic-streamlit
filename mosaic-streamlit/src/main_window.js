import path from 'path'
import { BrowserWindow } from 'electron'


const newWindow = (options) => {
  const win = new BrowserWindow(options || {
    width: 800,
    height: 600,
    title: 'Tapestri Insights v4.0 b1',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      enableRemoteModule: true,
      nodeIntegration: true,
    }
  })
  win.on('page-title-updated', (event) => {
    event.preventDefault()
  })
  return win
}

export const createAnotherWindow = (appRuntime) => {
  const anotherWindow = newWindow()
  anotherWindow.loadURL(`http://localhost:${appRuntime.streamlit.port}/`)
}

export const settingsWindow = (parent) => {
  const windowOptions = {
    modal: false,
  }
  const settingsWindow = new BrowserWindow({
    parent: parent,
    show: false,
    width: 400,
    height: 400,
    title: 'Settings',
    ...windowOptions,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      enableRemoteModule: true,
      nodeIntegration: true
    }
  })
  settingsWindow.loadURL(SETTINGS_WEBPACK_ENTRY)
  settingsWindow.removeMenu()
  settingsWindow.once('ready-to-show', () => {
    settingsWindow.setClosable(true)
    settingsWindow.show()
  })
  return settingsWindow
}

export const aboutWindow = (parent) => {
  let windowOptions = {}
  if (process.platform == "win32" || process.platform == "linux") {
    windowOptions = {...windowOptions, modal: true}
  } else if (process.platform == "darwin") {
    windowOptions = {...windowOptions, frame: false, titleBarStyle: 'hiddenInset'}
  }

  const aboutWindow = newWindow({
    parent: parent,
    show: false,
    width: 400,
    height: 400,
    title: 'Tapestri Insights v4.0 b1',
    ...windowOptions,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      enableRemoteModule: true,
      nodeIntegration: true
    }
  })
  aboutWindow.loadURL(ABOUT_WEBPACK_ENTRY)
  aboutWindow.removeMenu()
  aboutWindow.once('ready-to-show', () => {
    aboutWindow.setClosable(true)
    aboutWindow.show()
  })
  return aboutWindow
}

export default newWindow
