const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getDataPort: () => ipcRenderer.invoke('getDataPort'),
  getFramesPort: () => ipcRenderer.invoke('getFramesPort'),
  onSetPort: (callback) => ipcRenderer.on('setPort', callback),
});
