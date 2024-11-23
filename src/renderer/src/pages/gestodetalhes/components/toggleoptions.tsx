interface ToggleOptionsProps {
    toggle: boolean;
    tempoPressionado: number;
    onToggleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    onTempoChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ToggleOptions: React.FC<ToggleOptionsProps> = ({ toggle, tempoPressionado, onToggleChange, onTempoChange }) => {
    const handleTempoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = Math.max(1, Math.min(60, Number(event.target.value))); 
        onTempoChange({ ...event, target: { ...event.target, value: value.toString() } });
    };

    return (
        <div>
            <div className='toggle-options'>
                <h2>TOGGLE:</h2>
                <input
                    className='toggle-input'
                    type='checkbox'
                    checked={toggle}
                    onChange={onToggleChange}
                />
            </div>
            {toggle && (
                <div className='tempo-options'>
                    <h2>TEMPO PRESSIONADO:</h2>
                    <input
                        type='number'
                        min="1"
                        max="60"
                        value={tempoPressionado}
                        onChange={handleTempoChange}
                    />
                </div>
            )}
        </div>
    );
};

export default ToggleOptions;