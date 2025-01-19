import React, { useEffect, useState } from 'react';
import WebSocketClient from '../../network/websocket/websocket_client';
import './selectcamera.css';

interface Ports {
    data_port: number;
}

interface SelectCameraProps {
    onNavigate: (page: 'home') => void;
}

const SelectCamera: React.FC<SelectCameraProps> = ({ onNavigate }) => {
    const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [loadingText, setLoadingText] = useState<string>("Carregando.");
    const [error, setError] = useState<boolean>(false);
    const [errorCount, setErrorCount] = useState<number>(0);
    const [camerasDisponiveis, setCamerasDisponiveis] = useState<string[]>([]);
    const [selectedCamera, setSelectedCamera] = useState<string>('');

    useEffect(() => {
        const fetchPorts = async () => {
            try {
                const port = await window.electron.getDataPort();
                setPorts({ data_port: port });
            } catch (error) {
                console.error("Erro ao buscar a porta:", error);
                setError(true);
                setIsLoading(false);
            }
        };

        fetchPorts();

        return () => {
            if (wsClient) wsClient.close();
            setWsClient(null);
        };
    }, []);

    useEffect(() => {
        if (ports) {
            connectWebSocket();
        }
    }, [ports]);

    useEffect(() => {
        let intervalId: NodeJS.Timeout;

        if (isLoading) {
            intervalId = setInterval(() => {
                setLoadingText((prev) => {
                    return prev.endsWith("...") ? "Carregando." : prev + ".";
                });
            }, 500);
        } else {
            setLoadingText("Carregando.");
        }

        return () => clearInterval(intervalId);
    }, [isLoading]);

    const connectWebSocket = async () => {
        if (!ports) {
            console.log("Não foi possível encontrar a porta para o data.");
            setWsClient(null);
            setError(true);
            setIsLoading(false);
            return;
        }

        const client = new WebSocketClient(`http://localhost:${ports.data_port}`)

        setIsLoading(true);

        try {
            const success = await client.waitForConnection();
            if (!success) {
                throw new Error("Falha na conexão com o WebSocket.");
            }
            setWsClient(client);
            setError(false);

            client.sendGetCamerasDisponiveis();

            console.log("Esperando pelas cameras disponiveis.");

            client.handleCameraList = (camerasList: string[]) => {
                console.log("Cameras disponiveis recebidas. ", camerasList);
                setCamerasDisponiveis(camerasList);
                setIsLoading(false);
            };
        } catch (err) {
            console.error("Falha ao conectar ao WebSocket:", err);
            setError(true);
            setIsLoading(false);
            setWsClient(null);
        }
    };

    const tentarNovamente = () => {
        if (errorCount >= 3) {
            setErrorCount(0);
            alert("Em caso de erros constantes, tente executar o LibrasController com privilégios de administrador :)");
        } else {
            setErrorCount((prev) => prev + 1);
            connectWebSocket();
        }
    };

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedCamera(event.target.value);
    };

    const confirmarCamera = () => {
        if (!selectedCamera) {
            alert("Selecione uma câmera para continuar.");
            return;
        }

        if (wsClient) {
            try {
                wsClient.sendSetCamera(selectedCamera);
                wsClient.close();
                onNavigate('home');
            } catch {
                alert("Erro ao conectar ao servidor. Por favor, tente novamente.");
            }
        } else {
            alert("WebSocket não inicializado. Tente novamente.");
        }
    };

    return (
        <div className="container">
            <h1 className="title">LIBRASCONTROLLER</h1>
            <div id="select-container">
                {isLoading ? (
                    <p>{loadingText}</p>
                ) : (
                    <>
                        {error ? (
                            <>
                                <select id="select-camera" value="" disabled>
                                    <option value="" disabled hidden>
                                        Não foi possível encontrar câmeras disponíveis
                                    </option>
                                </select>
                                <button onClick={tentarNovamente} id="confirm-button">
                                    TENTAR NOVAMENTE
                                </button>
                            </>
                        ) : (
                            <>
                                <select id="select-camera" value={selectedCamera} onChange={handleChange}>
                                    <option value="" disabled hidden>
                                        Selecione uma câmera...
                                    </option>
                                    {camerasDisponiveis.map((camera, index) => (
                                        <option key={index} value={camera}>
                                            {camera}
                                        </option>
                                    ))}
                                </select>
                                <button onClick={confirmarCamera} id="confirm-button">
                                    CONFIRMAR
                                </button>
                            </>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default SelectCamera;
