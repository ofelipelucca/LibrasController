const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getPort: () => ipcRenderer.invoke('get-port'),

  onSetPort: (callback) => ipcRenderer.on('set-port', (event, ports) => callback(event, ports)),
});
