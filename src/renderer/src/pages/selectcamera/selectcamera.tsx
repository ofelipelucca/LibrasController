import React, { useRef, useEffect, useState } from 'react';
import WebSocketClient from '../../network/websocket/websocket_client';
import './selectcamera.css';

interface Ports {
    data_port: number;
}

interface SelectCameraProps {
    onNavigate: (page: 'home') => void;
}

const SelectCamera: React.FC<SelectCameraProps> = ({ onNavigate }) => {
    const wsClient = useRef<WebSocketClient | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [camerasDisponiveis, setCamerasDisponiveis] = useState<string[]>([]);
    const [selectedCamera, setSelectedCamera] = useState<string>('');

    useEffect(() => {
        const handlePorts = async (event: any, ports: Ports) => {
            setPorts(ports);

            const uri = `http://localhost:${ports.data_port}`;
            const client = new WebSocketClient(uri);

            await client.waitForConnection(); 
            client.sendGetCamerasDisponiveis();

            client.handleCameraList = (camerasList: string[]) => {
                setCamerasDisponiveis(camerasList);
            };

            wsClient.current = client;
        };

        window.electron.onSetPort(handlePorts);

        return () => {
            if (wsClient.current) {
                wsClient.current.close();
                wsClient.current = null;
            }
        };
    }, []);

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedCamera(event.target.value);
    };

    return (
        <div className="container">
            <h1 className="title">LIBRASCONTROLLER</h1>
            <div id="select-container">
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
            </div>
        </div>
    );
};

export default SelectCamera;
