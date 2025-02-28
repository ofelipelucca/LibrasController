interface InfoGestoProps {
    onNavigate: (page: "home") => void;
}

export default function InfoGesto({onNavigate}: InfoGestoProps) {
    return (
        <div className="container">
            <h1>PREENCHA OS DADOS DO NOVO GESTO:</h1>
            <label>Nome do gesto:</label><input type="text" />
            <label>Bind:</label><select name="Bind" id="select-bind">Selecione uma bind...</select>
            <button>SALVAR</button>
        </div>
    )
}