export const Gradients = () => {
    return (
        <svg width="0" height="0" style={{position: "absolute"}} aria-hidden="true" focusable="false">
            <defs>
                <linearGradient id="accent-grad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" style={{stopColor: "var(--color-accent)"}} />
                    <stop offset="75%" style={{stopColor: "var(--color-accent-soft)"}} />
                </linearGradient>
            </defs>
        </svg>
    );
};
