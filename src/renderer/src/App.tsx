import React, { useState } from "react";
import SelectCamera from './pages/selectcamera/selectcamera'
import Home  from "./pages/home/home";

type Page = 'selectcamera' | 'home' | 'gestocustom' | 'gestodetalhes';

const App: React.FC = () => {
    const [currentPage, setCurrentPage] = useState<Page>('selectcamera');
    const [selectedGesto, setSelectedGesto] = useState<Gesto | null>(null);

    const navigate = (page: Page, gesto?: Gesto) => {
        setCurrentPage(page);
        if (gesto) setSelectedGesto(gesto);
    };

    return (
        <div>
            {currentPage === 'selectcamera' && <SelectCamera onNavigate={navigate} />}
            {currentPage === 'home' && <Home onNavigate={navigate} />}
        </div>
    );
};

export default App;