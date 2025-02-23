interface ErrorProps {
    tentarNovamente: () => void;
}

export default function ErrorContainer({tentarNovamente}: ErrorProps) {
    return (
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
    )
}