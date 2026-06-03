import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Itineraire  from './pages/Itineraire'
import Simulateur  from './pages/Simulateur'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { Flex } from '@chakra-ui/react'

function App() {
  return (
    <BrowserRouter>
      <Flex direction="column" minH="100vh">
                      <Navbar />
      
                      {/* Zone de contenu principale — s'étire pour pousser le footer vers le bas */}
                      <Flex direction="column" flex="1">
                          <Routes>
                              <Route path="/" element={<Home />} />
                              <Route path="/dashboard" element={<Dashboard />} />
                              <Route path="/itineraire" element={<Itineraire />} />
                              <Route path="/simulateur" element={<Simulateur />} />
                          </Routes>
                      </Flex>
      
                      <Footer />
                  </Flex>
    </BrowserRouter>
  )
}

export default App