import React, { useEffect, useState } from "react";
import './gestodetalhes.css';

interface GestoDetalhesProps {
    onNavigate: (page: 'home') => void;
    gesto: Gesto | null;
}

const GestoDetalhes: React.FC<GestoDetalhesProps> = ({ onNavigate, gesto }) => {
    const [is_custom, setIsCustom] = useState<boolean>(false);
    const [toggle, setToggle] = useState<boolean>(false);

    useEffect(() => {
        // nome_gesto = *Obter nome do gesto*
        if (!gesto) {
            onNavigate('home');
            return
        }
        setToggle(gesto.modo_toggle)
    }, []);

    const handleVoltar = () => {
        onNavigate('home');
    }

    return (
        <div className='container'>
            <button className='voltar-button' onClick={handleVoltar}>VOLTAR</button>
            {gesto ? (
                <>
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