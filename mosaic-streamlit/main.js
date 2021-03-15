// Modules to control application life and create native browser window
const {app, BrowserWindow} = require('electron')
const path = require('path')
const childProcess = require('child_process')
//const fs = require('fs')

//fs.writeFile('/Users/aljosa/log.txt', 'init log', (err) => {})
const log = (msg) => {
  //fs.appendFile('/Users/aljosa/log.txt', msg, (err) => {});
  console.log(msg)
}

app.commandLine.appendSwitch('lang', 'en_US.UTF-8')

var stMosaic

function createWindow () {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  stMosaic = childProcess.spawn(
    process.env.SHELL,
    ['-c', './run'],
    {cwd: path.join(__dirname, 'run'), detached: true, env: {'LC_ALL': 'en_US.UTF-8'}}
  )

  var newLine = true
  stMosaic.stdout.on('data', (data) => {
    log(`data: ${data}`)
    if(newLine) {
      stMosaic.stdin.write('\n')
      console.log('sent newline');
      newLine = false
    }
  });
  
  stMosaic.stderr.on('data', (data) => {
    log(`data: ${data}`)
    console.error('error', data.toString());
  });

  stMosaic.on('exit', (code) => {
    log(`data: ${data}`)
    console.log(`Child exited with code ${code}`);
  });

  setTimeout(() => {
    mainWindow.loadURL('http://localhost:10000/')
  }, 3000);

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('will-quit', function () {
  console.log('\nwill-quit\n\n', stMosaic.pid)
  //stMosaic.kill()
  //process.kill(stMosaic.pid);
  process.kill(-stMosaic.pid);
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
