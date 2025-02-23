import { useState, useEffect } from "react";

export const useLoadingText = (initialText: string, isLoading: boolean) => {
    const [loadingText, setLoadingText] = useState(initialText);

    useEffect(() => {
        if (!isLoading) {
            setLoadingText(initialText); 
            return;
        }

        const animateLoadingText = () => {
            setLoadingText((prevText) => {
                const textWithoutDots = prevText.replace(/\.*$/, ""); 
                const dots = (prevText.match(/\./g) || []).length; 
                return dots >= 3 ? textWithoutDots : prevText + ".";
            });
        };

        const intervalId = setInterval(animateLoadingText, 500);
        return () => clearInterval(intervalId); 
    }, [isLoading, initialText]);

    return loadingText;
};