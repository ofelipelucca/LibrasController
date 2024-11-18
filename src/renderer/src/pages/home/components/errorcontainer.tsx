function ErrorContainer({ error, connectWebSocket }: any) {
    if (!error) return null;
    return (
        <div className="errorContainer">
            <p>Erro ao carregar dados. Verifique sua conexão.</p>
            <button onClick={connectWebSocket}>Tentar novamente</button>
        </div>
    );
}

export default ErrorContainer;