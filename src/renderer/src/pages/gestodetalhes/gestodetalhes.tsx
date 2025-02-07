import React, { useEffect, useState } from "react";
import WebSocketClient from "renderer/src/network/websockets/websocket_client";
import './gestodetalhes.css';
import BindOptions from "./components/bindoptions";
import ToggleOptions from "./components/toggleoptions";

interface GestoDetalhesProps {
    onNavigate: (page: 'home') => void;
    nome_do_gesto: string | null;
    gesto: Gesto | null;
}

interface Port {
    data_port: number;
}

interface GestoEditado {
    nome: string;
    bind: string;
    modoToggle: boolean;
    tempoPressionado: number;
}

const allBindOptions = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2",
    "3", "4", "5", "6", "7", "8", "9", "enter", "esc", "tab", "shift", "ctrl",
    "alt", "backspace", "space", "left", "up", "right", "down", "m1", "m3", "m2"
];

const GestoDetalhes: React.FC<GestoDetalhesProps> = ({ onNavigate, nome_do_gesto, gesto }) => {
    const [wsDataClient, setWsDataClient] = useState<WebSocketClient | null>(null);
    const [port, setPort] = useState<Port | null>(null);
    const [bind, setBind] = useState<string>(gesto?.bind || "");
    const [toggle, setToggle] = useState<boolean>(gesto?.modo_toggle || false);
    const [tempoPressionado, setTempoPressionado] = useState<number>(
        gesto?.tempo_pressionado ? Math.max(1, Math.min(60, gesto.tempo_pressionado)) : 1
    );

    useEffect(() => {
        if (!gesto) {
            onNavigate('home');
        }
        const fetchPorts = async () => {
            try {
                const port = await window.electron.getDataPort();
                setPort({ data_port: port });
            } catch (error) {
                console.error("Erro ao buscar a porta:", error);
                onNavigate('home');
            }
        };

        fetchPorts();

        return () => closeClients();
    }, [gesto, onNavigate]);

    useEffect(() => {
        if (port) connectWebSocket(port);
    }, [port]);

    const connectWebSocket = async (port: Port) => {
        try {
            const client_data = new WebSocketClient(`http://localhost:${port.data_port}`);
            const dataConnection = await client_data.waitForConnection();
            if (!dataConnection) throw new Error("Falha na conexão.");
            setWsDataClient(client_data);
        } catch (err) {
            console.error("Erro ao conectar:", err);
        }
    };

    const closeClients = () => wsDataClient?.close();

    const handleToggleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setToggle(event.target.checked);
    };

    const handleBindChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setBind(event.target.value);
    };

    const handleTempoPressionadoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = Math.max(1, Math.min(60, Number(event.target.value)));
        setTempoPressionado(value);
    };

    const handleSalvar = () => {
        if (wsDataClient) {
            const novoGesto: GestoEditado = {
                nome: nome_do_gesto || "Sem Nome",
                bind,
                modoToggle: toggle,
                tempoPressionado
            };

            wsDataClient.sendSaveGesto(novoGesto, true);
            onNavigate('home');
        }
    };

    return (
        <div className='container'>
            <div className='header'>
                <button className='voltar-button' onClick={() => onNavigate('home')}>VOLTAR</button>
                <h1>{nome_do_gesto?.toUpperCase()}</h1>
                <button className='salvar-button' onClick={handleSalvar}>SALVAR</button>
            </div>
            <div className='options-container'>
                <BindOptions
                    allBindOptions={allBindOptions}
                    isCustomizable={gesto?.customizable || false}
                    bind={bind}
                    onBindChange={handleBindChange}
                />
                <ToggleOptions
                    toggle={toggle}
                    tempoPressionado={tempoPressionado}
                    onToggleChange={handleToggleChange}
                    onTempoChange={handleTempoPressionadoChange}
                />
            </div>
        </div>
    );
};

export default GestoDetalhes;