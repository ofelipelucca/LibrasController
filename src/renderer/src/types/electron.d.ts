declare global {
  interface Ports {
    data_port: number;
    frames_port: number;
  }

  interface Gesto {
    bind: string;
    modo_toggle: boolean;
    tempo_pressionado: number;
  }

  interface Window {
    electron: {
      getDataPort: () => Promise<number>; 
      getFramesPort: () => Promise<number>; 
      onSetPort: (callback: (event: any, ports: Ports) => void) => void;
    };
  }
}

export {};
