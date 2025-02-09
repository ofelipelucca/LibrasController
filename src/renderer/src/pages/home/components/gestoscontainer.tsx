export default function GestosContainer({ gestos, adicionarGesto, mostrarDetalhesGesto }: any) {
    return (
        <div className="gestos-container">
            <button onClick={adicionarGesto} className="add-button">
                ADICIONAR NOVO GESTO
                <img src="assets/icons/add_icon.png" alt="Add" className="icon" />
            </button>
            {Object.keys(gestos).map((key, index) => (
                <div key={index} className="gesto-item">
                    <span className="gesto-text">{`${key.toUpperCase()} → ${gestos[key].bind.toUpperCase()}`}</span>
                    <button onClick={() => mostrarDetalhesGesto(key, gestos[key])} className="icon-button">
                        <img src="assets/icons/see_details_icon.png" alt="Ver Detalhes" className="icon" />
                    </button>
                </div>
            ))}
        </div>
    );
}