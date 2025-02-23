interface VideoContainerProps {
    frame: string | null;
    isLoading: boolean;
    selectedCamera: string;
    camerasDisponiveis: string[];
    handleCameraChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
    loadingText: string;
}

export default function VideoContainer({
    frame,
    isLoading,
    selectedCamera,
    camerasDisponiveis,
    handleCameraChange,
    loadingText,
}: VideoContainerProps) {
    if (isLoading && !frame) {
        return (
            <div className="video-container">
                <p id="loading-text">{loadingText}</p>
            </div>
        );
    }

    return (
        <div className="video-container">
            {frame && (
                <img
                    src={`data:image/jpeg;base64,${frame}`}
                    alt="Video Stream"
                    className="video"
                />
            )}
            <select
                value={selectedCamera}
                onChange={handleCameraChange}
                className="select-camera"
            >
                {camerasDisponiveis.map((camera, index) => (
                    <option key={index} value={camera}>
                        {camera}
                    </option>
                ))}
            </select>
        </div>
    );
}