const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const findAvailablePort = require('./src/renderer/src/network/utils/findAvailablePort');

let window;
let pyprocess;

async function initializeApp() {
  try {
    const data_port = await findAvailablePort(8000, 8200);
    const frames_port = await findAvailablePort(8201, 8400);
    createMainWindow();
    startPython(data_port, frames_port);

    window.webContents.on('did-finish-load', () => {
      window.webContents.send('set-port', { data_port, frames_port });
    });

  } catch (error) {
    console.error('Erro ao encontrar uma porta disponível:', error);
    app.quit();
  }
}

function createMainWindow() {
  window = new BrowserWindow({
    title: 'LibrasController',
    width: 1280,
    height: 720,
    maximizable: false,
    resizable: false,
    backgroundColor: "#141414",
    titleBarStyle: 'default',
    autoHideMenuBar: true,
    icon: path.join(__dirname, 'favicon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      devTools: true,
      preload: path.join(__dirname, 'src/renderer/preload.js')
    }
  });

  window.loadURL(`file://${path.join(__dirname, '/build/index.html')}`);

  window.on('closed', () => {
    window = null;
  });
}

function startPython(port1, port2) {
  pyprocess = spawn('python', [path.join(__dirname, 'src/main/main.py'), port1.toString(), port2.toString()]);

  pyprocess.stdout.on('data', (data) => {
    console.log("Iniciando Python");
    console.log(`Output: ${data}`);
  });

  pyprocess.stderr.on('data', (data) => {
    console.error(`Erro: ${data}`);
  });

  pyprocess.on('close', (code) => {
    console.log(`Python fechou com o código: ${code}`);
    app.quit();
  });
}

let ports = {
  data_port: 8000,
  frames_port: 8201
};

ipcMain.handle('getDataPort', () => {
  return ports.data_port;
});

ipcMain.handle('getFramesPort', () => {
  return ports.frames_port;
});

ipcMain.handle('getPort', () => {
  return ports;
});

app.whenReady().then(() => {
  initializeApp();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    initializeApp();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pyprocess) {
      pyprocess.kill();
    }
    app.quit();
  }
});

app.on('before-quit', () => {
  if (pyprocess) {
    pyprocess.kill();
  }
});