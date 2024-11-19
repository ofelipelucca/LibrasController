import React, { useState, useEffect } from 'react';
import './home.css';
import WebSocketClient from 'renderer/src/network/websocket/websocket_client';
import GestosContainer from './components/gestoscontainer';
import VideoContainer from './components/videocontainer';
import ErrorContainer from './components/errorcontainer';

interface HomeProps {
    onNavigate: (page: 'gestocustom' | 'gestodetalhes', gesto?: Gesto) => void;
}

const Home: React.FC<HomeProps> = ({ onNavigate }) => {
    const [wsDataClient, setWsDataClient] = useState<WebSocketClient | null>(null);
    const [wsFramesClient, setWsFramesClient] = useState<WebSocketClient | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [loadingText, setLoadingText] = useState('Carregando...');
    const [error, setError] = useState(false);
    const [gestos, setGestos] = useState<{ [key: string]: Gesto }>({});
    const [camerasDisponiveis, setCamerasDisponiveis] = useState<string[]>([]);
    const [selectedCamera, setSelectedCamera] = useState('');
    const [frame, setFrame] = useState<string | null>(null);

    useEffect(() => {
        const fetchPorts = async () => {
            try {
                setLoadingText('Carregando as portas...');
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
            connectWebSocket(ports);
        }
    }, [ports]);

    useEffect(() => {
        if (wsDataClient && wsFramesClient) {
            setupHandlers(wsDataClient, wsFramesClient);
            fetchInitialData(wsDataClient, wsFramesClient);
        }
    }, [wsDataClient, wsFramesClient]);

    const connectWebSocket = async (ports: Ports) => {
        setLoadingText('Conectando aos servidores...');
        setIsLoading(true);

        try {
            const client_data = new WebSocketClient(`http://localhost:${ports.data_port}`);
            const client_frames = new WebSocketClient(`http://localhost:${ports.frames_port}`);

            const dataConnection = await client_data.waitForConnection();
            const framesConnection = await client_frames.waitForConnection();

            if (!dataConnection || !framesConnection) throw new Error('Falha na conexão.');

            setWsDataClient(client_data);
            setWsFramesClient(client_frames);
        } catch (err) {
            console.error('Erro ao conectar:', err);
            handleErrorState();
        }
    };

    const closeClients = async () => {
        wsDataClient?.close();
        if (wsFramesClient) {
            wsFramesClient.sendStopDetection();
            wsFramesClient.close();
        }
    };

    const setupHandlers = (dataClient: WebSocketClient, framesClient: WebSocketClient) => {
        dataClient.handleAllGestos = (gestosList: { [key: string]: Gesto }) => {
            setGestos(gestosList || {});
        };

        dataClient.handleCameraSelecionada = setSelectedCamera;
        dataClient.handleCameraList = setCamerasDisponiveis;

        framesClient.handleFrame = (frameBase64: string) => {
            setFrame(frameBase64 ? `data:image/jpeg;base64,${frameBase64}` : null);
            if (isLoading) setIsLoading(false);
            framesClient.sendGetFrame();
        };
    };

    const fetchInitialData = async (dataClient: WebSocketClient, framesClient: WebSocketClient) => {
        const requests: TimedRequest[] = [
            { delay: 50, method: () => dataClient.sendGetAllGestos() },
            { delay: 150, method: () => dataClient.sendGetCamera() },
            { delay: 250, method: () => dataClient.sendGetCamerasDisponiveis() },
            { delay: 350, method: () => framesClient.sendStartDetection() },
            { delay: 600, method: () => framesClient.sendGetFrame() },
        ];

        await doRequests(requests);
    };

    const doRequests = async (requests: TimedRequest[]) => {
        for (const req of requests) {
            await new Promise<void>(resolve => setTimeout(resolve, req.delay));
            req.method();
        }
    };

    const handleErrorState = () => {
        setError(true);
        setIsLoading(false);
        setWsDataClient(null);
        setWsFramesClient(null);
    };

    const handleNavigate = async (page: 'gestocustom' | 'gestodetalhes', gesto?: Gesto) => {
        await closeClients();
        onNavigate(page, gesto);
    };

    const handleCameraChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
        const requests: TimedRequest[] = [
            { delay: 50, method: () => wsFramesClient?.sendStopDetection() },
            { delay: 150, method: () => wsFramesClient?.sendSetCamera(event.target.value) },
            { delay: 250, method: () => wsFramesClient?.sendStartDetection() },
            { delay: 350, method: () => wsFramesClient?.sendGetFrame() },
        ];

        await doRequests(requests);
    };

    return (
        <div className="container">
            <div className="mainContent">
                <GestosContainer
                    gestos={gestos}
                    adicionarGesto={() => handleNavigate('gestocustom')}
                    mostrarDetalhesGesto={(gesto: Gesto) => handleNavigate('gestodetalhes', gesto)}
                />
                <VideoContainer
                    isLoading={isLoading}
                    frame={frame}
                    selectedCamera={selectedCamera}
                    camerasDisponiveis={camerasDisponiveis}
                    handleCameraChange={handleCameraChange}
                    error={error}
                    loadingText={loadingText}
                />
                <ErrorContainer error={error} connectWebSocket={() => connectWebSocket(ports!)} />
            </div>
        </div>
    );
};

export default Home;
