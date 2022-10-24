import styles from './Navbar.module.css';
import {Link} from 'react-router-dom';
import Container from './Container';

function Navbar() {
    return (
        <nav className={styles.navbar}>
            <Container>
                <ul className={styles.list}>
                    <li className={styles.item}>
                        <Link to="/ubs">Cadastro</Link>
                    </li>
                    <li className={styles.item}>
                        <Link to="/movimentacao">Movimentação</Link>
                    </li>
                    <li className={styles.item}>
                        <Link to="/relatorios">Relatórios</Link>
                    </li>
                </ul>
            </Container>
      </nav>
    )
}

export default Navbar