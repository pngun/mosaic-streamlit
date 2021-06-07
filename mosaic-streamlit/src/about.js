import { BrowserWindow } from 'electron'
import path from 'path'


const about = (parent) => {
  let aboutWindow
  let windowOptions = {}
  if (process.platform == "win32" || process.platform == "linux") {
    windowOptions = {...windowOptions, modal: true}
  } else if (process.platform == "darwin") {
    windowOptions = {...windowOptions, frame: false, titleBarStyle: 'hiddenInset'}
  }

  aboutWindow = new BrowserWindow({
    parent: parent,
    show: false,
    width: 400,
    height: 400,
    ...windowOptions
  })
  aboutWindow.loadFile(path.join(__dirname, 'about.html'))
  aboutWindow.removeMenu()
  aboutWindow.once('ready-to-show', () => {
    aboutWindow.setClosable(true)
    aboutWindow.show()
  })
}

console.log('load about')

export default about
