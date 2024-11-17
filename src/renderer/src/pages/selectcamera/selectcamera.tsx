import React, { useRef, useEffect, useState } from 'react';
import WebSocketClient from '../../network/websocket/websocket_client';
import './selectcamera.css'

interface SelectCameraProps {
    onNavigate: (page: 'home') => void;
}

const SelectCamera: React.FC<SelectCameraProps> = ({ onNavigate }) => {
    const wsClient = useRef<WebSocketClient | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    
    useEffect(() => {
        window.electron.onSetPort((event, ports: Ports) => {
            setPorts(ports);
            console.log("Portas recebidas: ", ports);
        });
    }, []);

    return (
        <div className='container'>
            <h1 className='title'>LIBRASCONTROLLER</h1>
            <div id='select-container'>
            </div>
        </div>
    )
}

export default SelectCamera;