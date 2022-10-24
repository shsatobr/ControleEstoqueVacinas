import styles from './Ubs.module.css'
import UbsForm from './UbsForm'

function Ubs() {
    return (
        // <LinkButton to="/movimentacao" text="Movimentação"/>
        <section>
            <div className={styles.ubs_container}>
                <h1>Cadastro de UBS</h1>
                <UbsForm btnText="Incluir"/>
            </div>    
        </section>
    )
}

export default Ubs
