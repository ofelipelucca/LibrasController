interface Gesto {
    bind: string;
    tempo_pressionado: number;
}

export default class WebSocketClient {
    public socket: WebSocket | null = null;
    public uri: string;
    public isConnected: boolean = false;
    protected reconnectAttempts: number = 0;
    protected maxReconnectAttempts: number = 5;
    protected pingIntervalId: any = null;
    protected PING_INTERVAL: number = 100000;

    constructor(uri: string) {
        this.uri = uri;
        this.connect();
    }

    protected connect() {
        this.socket = new WebSocket(this.uri);
        console.log("Tentando conectar ao servidor:", this.uri);
        this.setupListeners();
    }

    public close() {
        if (!this.socket) {
            console.log('O socket não está aberto.');
            return;
        }
        console.log('Fechando a conexão com o servidor:', this.uri);
        this.socket.close();
        this.socket = null;
        this.stopHeartbeat();
        this.reconnectAttempts = 0;
    }

    protected setupListeners() {
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

    protected handleMessage(data: string) {
        try {
            const message = JSON.parse(data);

            console.log(message);

            if (message.status) {
                console.log(`Status: ${message.message}`);
            }

            if (message.error) {
                console.error(`Erro: ${message.error}`)
            }

            if (message.pong) {
                console.log('Pong recebido.');
            }

            if (message.camerasDisponiveis) {
                this.handleCameraList(message.camerasDisponiveis);
            }

            if (message.allGestos) {
                this.handleAllGestos(message.allGestos);
            }

            if (message.gesto) {
                this.handleGesto(message.gesto);
            }

            if (message.cameraSelecionada) {
                this.handleCameraSelecionada(message.cameraSelecionada);
            }
        } catch (e) {
            console.error('Falha no JSON:', e);
        }
    }

    public handleCameraList(cameras: string[]) { }
    public handleAllGestos(gestosList: { [key: string]: Gesto }) { }
    public handleGesto(gesto: Gesto) { }
    public handleCustomizableState(is_custom: boolean) { }
    public handleCameraSelecionada(camera_selecionada: string) { }

    public sendStartDetection() {
        this.send({ START_DETECTION: true });
    }

    public sendStopDetection() {
        this.send({ STOP_DETECTION: true });
    }

    public sendStartCropHandMode() {
        this.send({ START_CROP_HAND_MODE: true });
    }

    public sendStopCropHandMode() {
        this.send({ STOP_CROP_HAND_MODE: true });
    }

    public sendGetAllGestos() {
        this.send({ GET_ALL_GESTOS: true });
    }

    public getGestoByName(nome: string) {
        this.send({ GET_GESTO_BY_NAME: nome });
    }

    public sendGetCustomizableState(nome: string) {
        this.send({ GET_CUSTOMIZABLE_STATE: nome });
    }

    public sendSaveGesto(gesto: object, sobreescrever: boolean) {
        this.send({ SAVE_GESTO: gesto, sobreescrever });
    }

    public sendSetCamera(nomeCamera: string) {
        this.send({ SET_CAMERA: nomeCamera });
    }

    public sendGetCamera() {
        this.send({ GET_CAMERA: true });
    }

    public sendGetCamerasDisponiveis() {
        this.send({ GET_CAMERAS_DISPONIVEIS: true });
    }

    protected send(data: object) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            const message = JSON.stringify(data)
            console.log("ENVIANDO:", message)
            this.socket.send(message);
        } else {
            console.warn('WebSocket não está aberto. Mensagem não enviada:', data);
        }
    }

    protected startHeartbeat() {
        this.pingIntervalId = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.send({ ping: true });
                console.log('Enviando ping ao servidor...');
            }
        }, this.PING_INTERVAL);
    }

    protected stopHeartbeat() {
        if (this.pingIntervalId) {
            clearInterval(this.pingIntervalId);
            this.pingIntervalId = null;
        }
    }
}