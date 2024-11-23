interface BindOptionsProps {
    allBindOptions: string[];
    isCustomizable: boolean;
    bind: string;
    onBindChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
}

const BindOptions: React.FC<BindOptionsProps> = ({ allBindOptions, isCustomizable, bind, onBindChange }) => (
    <div className='bind-options-container'>
        <h2>BIND:</h2>
        <select
            className='binds-select'
            value={bind}
            onChange={onBindChange}
            disabled={!isCustomizable}
        >
            {allBindOptions.map((option, index) => (
                <option key={index} value={option}>
                    {option}
                </option>
            ))}
        </select>
    </div>
);

export default BindOptions;