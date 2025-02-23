interface SelectProps {
    selectedCamera: string;
    handleChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
    camerasDisponiveis: string[];
    confirmarCamera: () => void;
}

export default function SelectContainer({selectedCamera, handleChange, camerasDisponiveis, confirmarCamera}: SelectProps) {
    return (
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
    )
}