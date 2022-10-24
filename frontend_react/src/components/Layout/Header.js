import styles from './Header.module.css'
import Logo from '../../img/logo.png'

function Header() {
    return (
        <header className={styles.header}>
            <div>
                <img src={Logo} alt="Logotipo" className={styles.logo}/>
            </div>
            <div className={styles.text}>Sistema de controle de estoque de vacinas</div>
            <div className={styles.text}>Secretária da Saúde</div>
        </header>
    )
}

export default Header