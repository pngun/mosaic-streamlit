import { Menu } from 'electron'
import { createAnotherWindow, settingsWindow, aboutWindow } from './main_window'


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
      { label: 'About', click: () => { aboutWindow(mainWindow) } },
      { label: 'Settings', click: () => { settingsWindow(mainWindow) } },
      { label: 'Quit', role: 'quit' },
    ]},
    { role: 'editMenu' },
  ]

  if (process.env.MOSAIC_STREAMLIT_DEBUG) {
    template.push(
      { role: 'viewMenu' },
      { label: 'Throw error', click: () => { throw 'Test error' } },
    )
  }
  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

export default setApplicationMenu
