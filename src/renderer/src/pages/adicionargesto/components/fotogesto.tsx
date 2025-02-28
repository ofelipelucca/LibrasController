interface FotoGestoProps {
    frame: string | null;
    handleTirarFoto: () => void;
}

export default function FotoGesto({frame, handleTirarFoto}: FotoGestoProps) {
    return (
        <div className="foto-content-container">
            <div className="cropped-video-container">
                {frame && (
                    <img
                        src={`data:image/jpeg;base64,${frame}`}
                        alt="Video Stream"
                        className="video"
                    />
                )}
                <div className="buttons">
                    <button id="voltar-button">VOLTAR</button>
                    <button onClick={handleTirarFoto} id="foto-button">TIRAR FOTO</button>
                </div>
            </div>
            <div className="tutorial-container">
                <h1>INSTRUÇÕES:</h1>
                <div className="li-container">
                    <li>Reproduza o gesto desejado com a mão direita.</li>
                    <li>Clique em "TIRAR FOTO".</li>
                    <li>Preencha as informações e clique em "SALVAR".</li>
                </div>
            </div>
        </div>
    )
}