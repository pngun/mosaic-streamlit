import { app, ipcMain } from 'electron'
import setApplicationMenu from './menu'
import createMainWindow from './main_window'
import runner from './runner'
import settings from 'electron-settings'
import setupSentry from './sentry'

settings.get('sentry.enabled').then((value) => {
  if(value !== false && process.env.MOSAIC_STREAMLIT_SENTRY_ENABLED !== 'false') {
    setupSentry()
  }
})
export const appRuntime = {}

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) { // eslint-disable-line global-require
  app.quit()
}

app.on('ready', async () => {
  const mainWindow = createMainWindow()
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY)

  let sentry_enabled = await settings.get('sentry.enabled')
  if (typeof(sentry_enabled) !== 'boolean') {
    sentry_enabled = sentry_enabled !== false
    await settings.set('sentry', {enabled: sentry_enabled})
  }
  const streamlit = runner(mainWindow, sentry_enabled)
  appRuntime['streamlit'] = streamlit

  setApplicationMenu(mainWindow, appRuntime)

  ipcMain.on('find-text', (event, text) => {
    if (text.length == 0) return
    mainWindow.webContents.findInPage(text)
  })

  ipcMain.handle('get-sentry-enabled', async () => {
    return await settings.get('sentry.enabled')
  })

  ipcMain.on('sentry-enabled', async (event, enabled) => {
    await settings.set('sentry', {enabled: enabled})
    let sentry_enabled = await settings.get('sentry.enabled')
    mainWindow.webContents.send('sentry-enabled', sentry_enabled);
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', function () {
  if(process.platform != "win32") {
    process.kill(-appRuntime.streamlit.pid)
  }
})
