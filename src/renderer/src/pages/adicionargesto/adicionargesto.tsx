interface AdicionarGestoProps {
    onNavigate: (page: 'home') => void;
}

const AdicionarGesto: React.FC<AdicionarGestoProps> = ({ onNavigate }) => {
    return (
        <div className="container">
            <h1>ADICIONAR GESTO</h1>
            <button onClick={() => onNavigate("home")}>VOLTAR</button>
        </div>
    );
}

export default AdicionarGesto;