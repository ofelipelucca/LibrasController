function VideoContainer({ isLoading, frame, selectedCamera, camerasDisponiveis, handleCameraChange, error, loadingText }: any) {
    if (isLoading) {
        return (
            <div className="videoContainer">
                {error ? (
                    <img src="assets/camera_off.png" alt="Câmera desconectada" className="video" />
                ) : (
                    <p id="loadingText">{loadingText}</p>
                )}
            </div>
        );
    }

    return (
        <div className="videoContainer">
            {frame ? (
                <>
                    <img src={frame} alt="Webcam" className="video" />
                    <select value={selectedCamera} onChange={handleCameraChange} className="selectCamera">
                        {camerasDisponiveis.map((camera: string, index: number) => (
                            <option key={index} value={camera}>
                                {camera}
                            </option>
                        ))}
                    </select>
                </>
            ) : null}
        </div>
    );
}

export default VideoContainer;