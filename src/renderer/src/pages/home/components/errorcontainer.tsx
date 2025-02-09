export default function ErrorContainer({ error, connectWebSocket }: any) {
    if (!error) return null;
    return (
        <div className="error-container">
            <p>Erro ao carregar dados. Verifique sua conexão.</p>
            <button onClick={connectWebSocket}>Tentar novamente</button>
        </div>
    );
}