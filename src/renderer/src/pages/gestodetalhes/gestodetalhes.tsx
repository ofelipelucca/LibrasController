import React, { useEffect, useState } from "react";
import WebSocketClient from "renderer/src/network/websocket/websocket_client";
import './gestodetalhes.css';

interface GestoDetalhesProps {
    onNavigate: (page: 'home') => void;
    nome_do_gesto: string | null;
    gesto: Gesto | null;
}

const GestoDetalhes: React.FC<GestoDetalhesProps> = ({ onNavigate, nome_do_gesto, gesto }) => {
    const [wsDataClient, setWsDataClient] = useState<WebSocketClient | null>(null);
    const [ports, setPorts] = useState<Ports | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [loadingText, setLoadingText] = useState('Carregando...');
    const [error, setError] = useState(false);
    const [is_custom, setIsCustom] = useState<boolean>(false);
    const [toggle, setToggle] = useState<boolean>(false);

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
        if (!gesto) {
            onNavigate('home');
            return
        }
        //let nome_gesto = wsDataClient.sendGetGesto();
        setToggle(gesto.modo_toggle)
    }, [wsDataClient]);

    const closeClients = async () => {
        wsDataClient?.close();
    };

    const handleErrorState = () => {
        setError(true);
        setIsLoading(false);
        setWsDataClient(null);
    };

    const handleVoltar = () => {
        onNavigate('home');
    }

    return (
        <div className='container'>
            <button className='voltar-button' onClick={handleVoltar}>VOLTAR</button>
            {gesto ? (
                <>
                    <h1>{nome_do_gesto}</h1>
                    <h1>BIND: {gesto.bind}</h1>
                    {toggle ? (
                        <>
                            <h2>TOGGLE: ativado</h2>
                            <h2>TEMPO PRESSIONADO: {gesto.tempo_pressionado}</h2>
                        </>
                    ) : (
                        <>
                            <h2>TOGGLE: desativado</h2>
                        </>
                    )}
                </>
            ) : null}
        </div>
    );
}

export default GestoDetalhes;