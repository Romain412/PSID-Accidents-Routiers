import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// 1. On importe le Provider ET defaultSystem
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'

import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* 2. On donne le système par défaut au Provider */}
    <ChakraProvider value={defaultSystem}>
      <App />
    </ChakraProvider>
  </StrictMode>,
)