import classes from "./styles.module.css";

export const HotBar = () => {
    return (
        <section className={classes["hotbar"]}>
            <p>Reportes rápidos</p>
            <div className={classes["actions"]}>
                <button>Ejecutivo</button>
            </div>
        </section>
    );
};
