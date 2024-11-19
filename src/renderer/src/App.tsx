import React, { useState } from "react";
import SelectCamera from './pages/selectcamera/selectcamera'
import Home  from "./pages/home/home";
import GestoDetalhes from "./pages/gestodetalhes/gestodetalhes";

type Page = 'selectcamera' | 'home' | 'gestocustom' | 'gestodetalhes';

const App: React.FC = () => {
    const [currentPage, setCurrentPage] = useState<Page>('selectcamera');
    const [selectedGesto, setSelectedGesto] = useState<Gesto | null>(null);

    const navigate = (page: Page, gesto?: Gesto) => {
        if (page === 'gestodetalhes' && !gesto) {
            console.error("Erro: Tentativa de acessar 'gestodetalhes' sem um gesto válido.");
            return;
        }
    
        setCurrentPage(page);
        if (gesto) setSelectedGesto(gesto);
    };

    return (
        <div>
            {currentPage === 'selectcamera' && <SelectCamera onNavigate={navigate} />}
            {currentPage === 'home' && <Home onNavigate={navigate} />}
            {currentPage === 'gestodetalhes' && <GestoDetalhes onNavigate={navigate} gesto={selectedGesto} />}
        </div>
    );
};

export default App;