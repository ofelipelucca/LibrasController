function GestosContainer({ gestos, adicionarGesto, mostrarDetalhesGesto }: any) {
    return (
        <div className="gestosContainer">
            <button onClick={adicionarGesto} className="addButton">
                ADICIONAR NOVO GESTO
                <img src="assets/icons/add_icon.png" alt="Add" className="icon" />
            </button>
            {Object.keys(gestos).map((key, index) => (
                <div key={index} className="gestoItem">
                    <span className="gestoText">{`${key.toUpperCase()} → ${gestos[key].bind.toUpperCase()}`}</span>
                    <button onClick={() => mostrarDetalhesGesto(key, gestos[key])} className="iconButton">
                        <img src="assets/icons/see_details_icon.png" alt="Ver Detalhes" className="icon" />
                    </button>
                </div>
            ))}
        </div>
    );
}

export default GestosContainer;