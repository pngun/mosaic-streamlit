const { ipcRenderer, contextBridge } = require('electron')

window.addEventListener('DOMContentLoaded', () => {
  var searchBox = document.createElement('input')
  searchBox.setAttribute("id", "search-box");
  searchBox.style.cssText = 'display:none;position:absolute;top:10px;left:50%;border:2px solid #000;z-index:100;width:100px;height:20px'
  document.body.appendChild(searchBox)

  searchBox.addEventListener('change', () => {
    const result = document.getElementById('search-box').value
    ipcRenderer.send('find-text', result)
  })
})

ipcRenderer.on('toggle-find', () => {
  const search = document.getElementById('search-box')
  if (search.style.display === 'block') {
    search.style.display = 'none'
  } else {
    search.style.display = 'block'
    search.focus()
  }
})

const setSentry = (enabled) => {
  console.log('setSentry', enabled)
  ipcRenderer.send('sentry-enabled', enabled)
}

contextBridge.exposeInMainWorld('_app', {
  setSentry,
  isSentryEnabled: async () => {
    return await ipcRenderer.invoke('get-sentry-enabled')
  },
})
console.log('end preload')
