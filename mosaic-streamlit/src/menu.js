import { Menu } from 'electron'
import { createAnotherWindow, settingsWindow } from './main_window'
import createAboutWindow from './about'


const setApplicationMenu = (mainWindow) => {
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
      { label: 'About', click: () => { createAboutWindow(mainWindow) } },
      { label: 'Settings', click: () => { settingsWindow(mainWindow) } },
      { label: 'Quit', role: 'quit' },
    ]},
    { role: 'editMenu' },
    { role: 'viewMenu' },
  ]
  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

export default setApplicationMenu
