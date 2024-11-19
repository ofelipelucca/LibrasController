import React, { useState } from "react";
import SelectCamera from './pages/selectcamera/selectcamera';
import Home from "./pages/home/home";
import GestoDetalhes from "./pages/gestodetalhes/gestodetalhes";

type Page = 'selectcamera' | 'home' | 'gestocustom' | 'gestodetalhes';

const App: React.FC = () => {
    const [currentPage, setCurrentPage] = useState<Page>('selectcamera');
    const [selectedGestoName, setSelectedGestoName] = useState<string | null>(null);
    const [selectedGestoObject, setSelectedGestoObject] = useState<Gesto | null>(null);

    const navigate = (page: Page, nome_do_gesto?: string, gesto?: Gesto) => {
        if (page === 'gestodetalhes' && (!nome_do_gesto || !gesto)) {
            console.error("Erro: Tentativa de acessar 'gestodetalhes' sem um gesto válido.");
            return;
        }

        setCurrentPage(page);

        if (nome_do_gesto) setSelectedGestoName(nome_do_gesto);
        if (gesto) setSelectedGestoObject(gesto);
    };

    return (
        <div>
            {currentPage === 'selectcamera' && <SelectCamera onNavigate={navigate} />}
            {currentPage === 'home' && <Home onNavigate={navigate} />}
            {currentPage === 'gestodetalhes' && (
                <GestoDetalhes
                    onNavigate={navigate}
                    nome_do_gesto={selectedGestoName}
                    gesto={selectedGestoObject}
                />
            )}
        </div>
    );
};

export default App;