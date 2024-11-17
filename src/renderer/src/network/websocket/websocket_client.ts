interface Gesto {
    bind: string;
    tempo_pressionado: number;
}

class WebSocketClient {
    public socket: WebSocket | null = null;
    public uri: string;
    public isConnected: boolean = false;
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number = 5;
    private pingIntervalId: any = null;
    private PING_INTERVAL: number = 10000;

    constructor(uri: string) {
        this.uri = uri;
        this.connect();
    }

    private connect() {
        this.socket = new WebSocket(this.uri);
        console.log("Tentando conectar ao servidor:", this.uri);
        this.setupListeners();
    }

    public close() {
        if (this.socket) {
            console.log('Fechando a conexão com o servidor:', this.uri);
            this.socket.close();
            this.socket = null;
        }
        this.stopHeartbeat();
        this.reconnectAttempts = 0;
    }

    private setupListeners() {
        if (!this.socket) return;

        this.socket.onopen = () => {
            console.log('Conectado ao servidor:', this.uri);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.startHeartbeat();
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(event.data);
        };

        this.socket.onclose = () => {
            console.log('Desconectado do servidor:', this.uri);
            this.isConnected = false;
            this.stopHeartbeat();
        };
        
        this.socket.onerror = (error) => {
            console.error('Erro no WebSocket:', error);
        };
    }

    public waitForConnection(timeoutMs: number = 5000): Promise<boolean> {
        return new Promise((resolve, reject) => {
            if (this.isConnected) {
                resolve(true);
                return;
            }

            const timeout = setTimeout(() => {
                console.warn('Timeout ao tentar conectar ao WebSocket.');
                reject(false);
            }, timeoutMs);

            if (this.socket) {
                const onOpen = (event: Event) => {
                    clearTimeout(timeout);
                    this.isConnected = true;
                    resolve(true);
                };

                const onClose = (event: CloseEvent) => {
                    clearTimeout(timeout);
                    console.warn('Conexão fechada antes de conectar.', event);
                    reject(false);
                };

                const onError = (error: Event) => {
                    clearTimeout(timeout);
                    console.error('Erro ao conectar ao WebSocket.', error);
                    reject(false);
                };

                this.socket.addEventListener("open", onOpen);
                this.socket.addEventListener("close", onClose);
                this.socket.addEventListener("error", onError);

                const cleanup = () => {
                    if (this.socket) {
                        this.socket.removeEventListener("open", onOpen);
                        this.socket.removeEventListener("close", onClose);
                        this.socket.removeEventListener("error", onError);
                    }
                };

                resolve = ((originalResolve) => {
                    return (...args) => {
                        cleanup();
                        originalResolve(...args);
                    };
                })(resolve);

                reject = ((originalReject) => {
                    return (...args) => {
                        cleanup();
                        originalReject(...args);
                    };
                })(reject);
            } else {
                clearTimeout(timeout);
                reject(false);
            }
        });
    }

    private handleMessage(data: string) {
        try {
            const message = JSON.parse(data);

            if (message.status) {
                console.log(`Status: ${message.message}`);
            }

            if (message.pong) {
                console.log('Pong recebido.');
            }

            if (message.cameras_disponiveis) {
                this.handleCameraList(message.cameras_disponiveis);
            }

            if (message.allBinds) {
                this.handleBindsList(message.allBinds);
            }

            if (message.camera_selecionada) {
                this.handleCameraSelecionada(message.camera_selecionada);
            }

            if (message.frame) {
                this.handleFrame(message.frame);
            }
        } catch (e) {
            console.error('Falha no JSON:', e);
        }
    }

    public handleCameraList(cameras: string[]) { }
    public handleBindsList(bindsList: { [key: string]: Gesto }) { }
    public handleCameraSelecionada(camera_selecionada: string) { }
    public handleFrame(frame: string) { }

    public sendStartDetection() {
        this.send({ startDetection: true });
    }

    public sendGetAllBinds() {
        this.send({ getAllBinds: true });
    }

    public sendGetGesto(nome: string) {
        this.send({ getGesto: nome });
    }

    public sendSaveGesto(gesto: object, sobreescrever: boolean) {
        this.send({ saveGesto: gesto, sobreescrever });
    }

    public sendSetCamera(nomeCamera: string) {
        this.send({ setCamera: nomeCamera });
    }

    public sendGetCamera() {
        this.send({ getCamera: true });
    }

    public sendGetCamerasDisponiveis() {
        this.send({ getCamerasDisponiveis: true });
    }

    public sendGetFrame() {
        this.send({ getFrame: true });
    }

    private send(data: object) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket não está aberto. Mensagem não enviada:', data);
        }
    }

    private tryReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const timeout = Math.pow(2, this.reconnectAttempts) * 1000;
            setTimeout(() => {
                this.reconnectAttempts++;
                console.log(`Tentando reconectar... Tentativa ${this.reconnectAttempts}`);
                this.connect();
            }, timeout);
        } else {
            console.error(`Falha ao reconectar após ${this.reconnectAttempts} tentativas.`);
        }
    }

    private startHeartbeat() {
        this.pingIntervalId = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.send({ ping: true });
                console.log('Enviando ping ao servidor...');
            }
        }, this.PING_INTERVAL);
    }

    private stopHeartbeat() {
        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
            this.pingIntervalId = null;
        }
    }
}

export default WebSocketClient;
