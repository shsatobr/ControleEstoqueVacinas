import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';


// Importações das opções do menu
import Ubs from './components/pages/cadastros/Ubs';
import Movimentacao from './components/pages/cadastros/Usuarios';
import Vacinas from './components/pages/cadastros/Vacinas';


import Container from './components/Layout/Container';
import Footer from './components/Layout/Footer';
import Navbar from './components/Layout/Navbar';
import Header from './components/Layout/Header';

function App() {
  return (
    <Router>
      <Header/>
      <Navbar/>
      <Container customClass="min-height">        
        <Routes>
          <select>Cadastro
            <option>UBS</option>
            <option>Usuários</option>
            <option>Vacinas</option>
          </select>
          <Route path="/ubs" element={<Ubs/>}/>
          <Route path="/movimentacao" element={<Movimentacao/>}/>
          <Route path="/relatorios" element={<Vacinas/>}/>
        </Routes>
      </Container>
      <Footer/>
    </Router>

  );
}

export default App;