import React, { useEffect, useState, useRef } from "react";
import './adicionargesto.css';
import WebSocketClient from "renderer/src/network/websockets/websocket_client";
import WebSocketFrames from "renderer/src/network/websockets/websocket_frames";
import { useLoadingText } from "renderer/src/hooks/useLoadingText";

interface AdicionarGestoProps {
    onNavigate: (page: 'home') => void;
}

const AdicionarGesto: React.FC<AdicionarGestoProps> = ({ onNavigate }) => {
    const wsDataClientRef = useRef<WebSocketClient | null>(null);
    const [wsDataClient, setWsDataClient] = useState<WebSocketClient | null>(null);
    const [wsFramesClient, setWsFramesClient] = useState<WebSocketFrames | null>(null);
    const [frame, setFrame] = useState<string | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const loadingText = useLoadingText("Preparando tudo", isLoading);
    const [error, setError] = useState(false);

    useEffect(() => {
        const fetchPorts = async () => {
            try {
                const data_port = await window.electron.getDataPort();
                const frames_port = await window.electron.getFramesPort();
                setPorts({ data_port, frames_port });
            } catch (err) {
                console.error('Erro ao buscar as portas:', err);
                handleErrorState();
            }
        };

        fetchPorts();

        return () => {
            closeClients();
        };
    }, []);

    useEffect(() => {
        if (ports) {
            connectWebSockets(ports);
        }
    }, [ports]);

    const connectWebSockets = async (ports: Ports) => {
        setIsLoading(true);

        try {
            const client_data = new WebSocketClient(`http://localhost:${ports.data_port}`);
            const dataConnection = await client_data.waitForConnection();

            const client_frames = new WebSocketFrames(`http://localhost:${ports.frames_port}`);
            const framesConnection = await client_frames.waitForConnection();

            if (!framesConnection || !dataConnection) throw new Error('Falha na conexão');

            setWsDataClient(client_data);
            wsDataClientRef.current = client_data;
            setWsFramesClient(client_frames);
        } catch (err) {
            console.error('Erro ao conectar:', err);
            handleErrorState();
        }
    };

    useEffect(() => {
        if (wsDataClient && wsFramesClient) {
            fetchInitialData(wsDataClient);
            setupHandlers(wsFramesClient);
        }
    }, [wsDataClient, wsFramesClient]);

    const closeClients = async () => {
        console.log("Fechando client de data.");
        if (wsDataClientRef.current) {
            wsDataClientRef.current.sendStopCropHandMode();
            wsDataClientRef.current.sendStopDetection();
            wsDataClientRef.current.close();
            wsDataClientRef.current = null;
        }
        setWsDataClient(null);
    };

    const setupHandlers = (framesClient: WebSocketFrames) => {
        framesClient.handleFrame = setFrame;
    };

    const fetchInitialData = async (dataClient: WebSocketClient) => {
        console.log("Enviando requests iniciais...");
        const requests: TimedRequest[] = [
            { delay: 50, method: () => dataClient.sendStartCropHandMode() },
            { delay: 100, method: () => dataClient.sendStartDetection() },
        ];

        await doRequests(requests);
    };

    const doRequests = async (requests: TimedRequest[]) => {
        for (const req of requests) {
            await new Promise<void>(resolve => setTimeout(resolve, req.delay));
            req.method();
        }
    };

    useEffect(() => {
        if (frame && isLoading) setIsLoading(false);
    }, [frame]);

    const handleErrorState = () => {
        setError(true);
        setIsLoading(false);
        setWsDataClient(null);
        wsDataClientRef.current = null;
    };

    const handleTirarFoto = () => {
        console.log('Tirou foto!!!!! (:');
    }

    if (isLoading) {
        return (
            <div className="loading-container">
                <p id="loadingText">{loadingText}</p>
            </div>
        );
    }

    return (
        <div className="content-container">
            <div className="video-container">
                {frame && (
                    <img
                        src={`data:image/jpeg;base64,${frame}`}
                        alt="Video Stream"
                        className="video"
                    />
                )}
                <div className="buttons">
                    <button onClick={() => onNavigate("home")} id="voltar-button">VOLTAR</button>
                    <button onClick={handleTirarFoto} id="foto-button">TIRAR FOTO</button>
                </div>
            </div>
        </div>
    );
}

export default AdicionarGesto;