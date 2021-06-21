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


  const addMontserratFont = () => {
    var google_fonts = document.createElement('link')
    google_fonts.rel = 'preconnect'
    google_fonts.href = 'https://fonts.gstatic.com'
    document.getElementsByTagName('head')[0].appendChild(google_fonts)

    var link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap'
    document.getElementsByTagName('head')[0].appendChild(link)

    var css = '* { font-family: "Montserrat", sans-serif !important; }'
    const style = document.createElement('style');
    document.getElementsByTagName('head')[0].appendChild(style)
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
  }
  addMontserratFont()
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
