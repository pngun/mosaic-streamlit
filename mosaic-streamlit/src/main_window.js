//const {
  //app, ipcMain, webContents, globalShortcut, Menu, MenuItem, BrowserWindow
//} = require('electron')
import path from 'path'
import { BrowserWindow } from 'electron'

const newWindow = () => {
  return new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      enableRemoteModule: true,
      nodeIntegration: true,
    }
  })
}

export const createAnotherWindow = () => {
  const anotherWindow = newWindow()
  anotherWindow.loadURL('http://localhost:10000/')
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
    ...windowOptions,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      enableRemoteModule: true,
      nodeIntegration: true
    }
  })
  settingsWindow.loadURL(SETTINGS_WEBPACK_ENTRY)
  //settingsWindow.removeMenu()
  settingsWindow.once('ready-to-show', () => {
    settingsWindow.setClosable(true)
    settingsWindow.show()
  })
  return settingsWindow
}


export default newWindow
