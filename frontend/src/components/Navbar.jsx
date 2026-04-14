import { useState } from 'react'
import {
  Box,
  Flex,
  Text,
  IconButton,
  Button,
  Container,
  HStack,
  VStack,
} from '@chakra-ui/react'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { LuMenu, LuX, LuLayers } from "react-icons/lu"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()

  const toggleMenu = () => setIsOpen(!isOpen)

  // Design des liens revu : Style "Pilule" très doux au survol et à l'état actif
  const NavLink = ({ children, to }) => {
    const isActive = location.pathname === to
    return (
      <Text
        as={RouterLink}
        to={to}
        px="4"
        py="2"
        borderRadius="full"
        fontSize="sm"
        fontWeight={isActive ? "bold" : "medium"}
        color={isActive ? "blue.700" : "gray.600"}
        bg={isActive ? "blue.50" : "transparent"}
        _hover={{
          bg: isActive ? "blue.100" : "gray.50",
          color: isActive ? "blue.800" : "gray.900"
        }}
        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
      >
        {children}
      </Text>
    )
  }

  return (
    <Box
      as="nav"
      position="sticky"
      top="0"
      zIndex="100"
      bg="rgba(255, 255, 255, 0.85)"
      backdropFilter="blur(16px)"
      borderBottom="1px solid"
      borderColor="blackAlpha.50"
      boxShadow="sm"
      transition="all 0.3s"
    >
      <Container maxW="container.xl">
        <Flex h="20" alignItems="center" justifyContent="space-between">
          
          {/* LOGO : Ajout d'un léger zoom au survol et d'un dégradé sur l'icône */}
          <HStack as={RouterLink} to="/" gap="3" role="group">
            <Flex 
              w="10" h="10" 
              bgGradient="to-br"
              gradientFrom="blue.500"
              gradientTo="blue.700"
              color="white" 
              borderRadius="xl" 
              alignItems="center" 
              justifyContent="center" 
              boxShadow="md"
              transition="transform 0.2s"
              _groupHover={{ transform: 'scale(1.05)' }}
            >
              <LuLayers size="22" />
            </Flex>
            <Text 
              fontSize="2xl" 
              fontWeight="black" 
              color="gray.800"
              letterSpacing="tighter"
            >
              Data<Text as="span" color="blue.600">Vision</Text>
            </Text>
          </HStack>

          {/* DESKTOP NAV */}
          <HStack display={{ base: 'none', md: 'flex' }} gap="2">
            <NavLink to="/">Accueil</NavLink>
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/stats">Statistiques</NavLink>
          </HStack>

          {/* ACTIONS (Boutons affinés) */}
          <HStack gap="4">
            <Button 
              display={{ base: 'none', md: 'inline-flex' }} 
              variant="ghost" 
              color="gray.600"
              fontWeight="medium"
              _hover={{ bg: 'gray.50', color: 'gray.900' }}
              borderRadius="full"
            >
              Connexion
            </Button>
            <Button 
              as={RouterLink} 
              to="/signup" 
              bg="blue.600" 
              color="white" 
              px="6" 
              borderRadius="full"
              fontWeight="bold"
              _hover={{ 
                bg: 'blue.700', 
                transform: 'translateY(-1px)',
                boxShadow: '0 4px 14px 0 rgba(49, 130, 206, 0.39)' // Ombre colorée
              }}
              _active={{ transform: 'translateY(0)' }}
              transition="all 0.2s"
            >
              Démarrer
            </Button>
            
            {/* BOUTON MENU MOBILE */}
            <IconButton
              display={{ base: 'flex', md: 'none' }}
              onClick={toggleMenu}
              variant="ghost"
              color="gray.700"
              fontSize="24px"
              aria-label="Ouvrir le menu"
              borderRadius="full"
              _hover={{ bg: 'gray.100' }}
            >
               {isOpen ? <LuX /> : <LuMenu />}
            </IconButton>
          </HStack>
        </Flex>

        {/* MOBILE MENU (Mieux espacé et interactif) */}
        {isOpen && (
          <VStack 
            display={{ md: 'none' }} 
            pb={6} 
            pt={2} 
            gap="2" 
            alignItems="stretch" 
            borderTop="1px solid" 
            borderColor="gray.100"
          >
            <Text as={RouterLink} to="/" onClick={toggleMenu} px="4" py="3" borderRadius="lg" _hover={{ bg: 'blue.50', color: 'blue.700' }} fontWeight="medium">Accueil</Text>
            <Text as={RouterLink} to="/dashboard" onClick={toggleMenu} px="4" py="3" borderRadius="lg" _hover={{ bg: 'blue.50', color: 'blue.700' }} fontWeight="medium">Dashboard</Text>
            <Text as={RouterLink} to="/stats" onClick={toggleMenu} px="4" py="3" borderRadius="lg" _hover={{ bg: 'blue.50', color: 'blue.700' }} fontWeight="medium">Statistiques</Text>
            <Button w="full" bg="gray.100" color="gray.800" borderRadius="xl" mt={4} size="lg" _hover={{ bg: 'gray.200' }}>Connexion</Button>
          </VStack>
        )}
      </Container>
    </Box>
  )
}