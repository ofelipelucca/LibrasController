import WebSocketClient from "./websocket_client";

export default class WebSocketFrames extends WebSocketClient {
    constructor(uri: string) {
        super(uri);
    }

    protected handleMessage(data: string) {
        try {
            const message = JSON.parse(data);

            if (message.frame) {
                this.handleFrame(message.frame);
            }
        } catch (e) {
            console.error('Falha no JSON:', e);
        }
    }

    public handleFrame(frame: string) { };
}