import React, { useState, useEffect, useRef } from 'react';
import './home.css';
import WebSocketClient from 'renderer/src/network/websocket/websocket_client';
import WebSocketFrames from 'renderer/src/network/websocket/websocket_frames';
import GestosContainer from './components/gestoscontainer';
import VideoContainer from './components/videocontainer';
import ErrorContainer from './components/errorcontainer';

interface HomeProps {
    onNavigate: (page: 'gestocustom' | 'gestodetalhes', nome_do_gesto?: string, gesto?: Gesto) => void;
}

const Home: React.FC<HomeProps> = ({ onNavigate }) => {
    const [wsDataClient, setWsDataClient] = useState<WebSocketClient | null>(null);
    const [wsFramesClient, setWsFramesClient] = useState<WebSocketFrames | null>(null);
    const [frame, setFrame] = useState<string | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [loadingText, setLoadingText] = useState('Carregando...');
    const [error, setError] = useState(false);
    const [gestos, setGestos] = useState<{ [nome_do_gesto: string]: Gesto }>({});
    const [camerasDisponiveis, setCamerasDisponiveis] = useState<string[]>([]);
    const [selectedCamera, setSelectedCamera] = useState('');

    useEffect(() => {
        const fetchPorts = async () => {
            try {
                setLoadingText('Carregando as portas.');
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
        setLoadingText('Abrindo a câmera.');
        setIsLoading(true);

        try {
            const client_data = new WebSocketClient(`http://localhost:${ports.data_port}`);
            const dataConnection = await client_data.waitForConnection();

            const client_frames = new WebSocketFrames(`http://localhost:${ports.frames_port}`);
            const framesConnection = await client_frames.waitForConnection();

            if (!framesConnection || !dataConnection) throw new Error('Falha na conexão');

            setWsDataClient(client_data);
            setWsFramesClient(client_frames);
        } catch (err) {
            console.error('Erro ao conectar:', err);
            handleErrorState();
        }
    };

    useEffect(() => {
        if (wsDataClient && wsFramesClient) {
            setupHandlers(wsDataClient, wsFramesClient);
            fetchInitialData(wsDataClient);
        }
    }, [wsDataClient, wsFramesClient]);

    const closeClients = async () => {
        console.log("Fechando client de data.");
        wsDataClient?.sendStopFramesStream();
        wsDataClient?.sendStopDetection();
        wsDataClient?.close();
    };

    const setupHandlers = (dataClient: WebSocketClient, framesClient: WebSocketFrames) => {
        dataClient.handleAllGestos = (gestosList: { [key: string]: Gesto }) => {
            setGestos({ ...gestosList });
        };
        dataClient.handleCameraSelecionada = setSelectedCamera;
        dataClient.handleCameraList = setCamerasDisponiveis;
        framesClient.handleFrame = setFrame;
    };

    const fetchInitialData = async (dataClient: WebSocketClient) => {
        console.log("Enviando requests iniciais...");
        const requests: TimedRequest[] = [
            { delay: 50, method: () => dataClient.sendGetAllGestos() },
            { delay: 150, method: () => dataClient.sendGetCamera() },
            { delay: 250, method: () => dataClient.sendGetCamerasDisponiveis() },
            { delay: 350, method: () => dataClient.sendStartDetection() },
            { delay: 450, method: () => dataClient.sendStartFrameStream() },
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
        let intervalId: NodeJS.Timeout;

        const animateLoadingText = (baseText: string) => {
            setLoadingText((prev) => {
                const dots = prev.replace(baseText, '').length;
                return dots >= 3 ? baseText : `${prev}.`;
            });
        };

        if (isLoading) {
            intervalId = setInterval(() => {
                if (loadingText.startsWith("Carregando")) {
                    animateLoadingText("Carregando");
                }
                if (loadingText.startsWith("Abrindo a câmera")) {
                    animateLoadingText("Abrindo a câmera");
                }
            }, 500);
        }

        return () => clearInterval(intervalId);
    }, [isLoading, loadingText]);

    useEffect(() => {
        if (frame && isLoading) setIsLoading(false);
    }, [frame]);

    const handleErrorState = () => {
        setError(true);
        setIsLoading(false);
        setWsDataClient(null);
    };

    const handleNavigate = async (page: 'gestocustom' | 'gestodetalhes', nome_do_gesto?: string, gesto?: Gesto) => {
        await closeClients();
        onNavigate(page, nome_do_gesto, gesto);
    };

    const handleCameraChange = () => {
        // TODO
    };

    return (
        <div className="container">
            <div className="mainContent">
                <GestosContainer
                    gestos={gestos}
                    adicionarGesto={() => handleNavigate('gestocustom')}
                    mostrarDetalhesGesto={(nome_do_gesto: string, gesto: Gesto) => handleNavigate('gestodetalhes', nome_do_gesto, gesto)}
                />
                <VideoContainer
                    frame={frame}
                    isLoading={isLoading}
                    selectedCamera={selectedCamera}
                    camerasDisponiveis={camerasDisponiveis}
                    handleCameraChange={handleCameraChange}
                    loadingText={loadingText}
                />
                <ErrorContainer error={error} connectWebSocket={() => connectWebSockets(ports!)} />
            </div>
        </div>
    );
};

export default Home;