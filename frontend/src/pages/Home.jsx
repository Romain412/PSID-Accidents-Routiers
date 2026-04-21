import { 
  Heading, 
  Text, 
  Container, 
  VStack, 
  Box, 
  SimpleGrid, 
  Icon, 
  Link, 
  Separator,
  Badge,
  Stack
} from '@chakra-ui/react'
import { LuChartColumnIncreasing, LuMap, LuDatabase, LuExternalLink, LuShieldAlert } from "react-icons/lu"

export default function Home() {
  return (
    <Container maxW="6xl" py={20}>
      <VStack spaceY={12} align="stretch">
        
        
        <VStack spaceY={4} align="center" textAlign="center">
          <Badge colorPalette="blue" variant="surface" px={3} py={1} borderRadius="full">
            Projet SI et Données (PSID) — 2025/2026
          </Badge>
          <Heading as="h1" size="6xl" fontWeight="black" letterSpacing="tight">
            ACCIDENTS <Text as="span" color="blue.500">ROUTIERS</Text>
          </Heading>
          <Text fontSize="xl" color="gray.600" maxW="2xl">
            Analyse exploratoire et visualisation interactive des accidents corporels 
            de la circulation en France basées sur les données officielles de l'ONISR.
          </Text>
        </VStack>

        <Separator />

        
        <SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>
          <FeatureCard 
            icon={LuDatabase} 
            title="Dataset 2024" 
            text="Exploitation du fichier national BAAC (Bulletin d'Analyse des Accidents Corporels)." 
          />
          <FeatureCard 
            icon={LuChartColumnIncreasing} 
            title="Dataviz" 
            text="Visualisation des facteurs aggravants : météo, luminosité et profils des usagers." 
          />
          <FeatureCard 
            icon={LuMap} 
            title="Géographie" 
            text="Analyse de la répartition spatiale et de la dangerosité par type de réseau routier." 
          />
        </SimpleGrid>

        
        <Box p={{ base: 6, md: 10 }} bg="blue.50" borderRadius="3xl" border="1px solid" borderColor="blue.100">
          <Stack direction={{ base: "column", md: "row" }} justify="space-between" align="center" gap={8}>
            <VStack align="flex-start" spaceY={4}>
              <Heading size="lg" display="flex" alignItems="center" gap={2}>
                <Icon as={LuShieldAlert} color="blue.600" />
                Origine des données
              </Heading>
              <Text color="gray.700">
                Ce dashboard s'appuie sur les données ouvertes publiées par le Ministère de l'Intérieur 
                sous Licence Ouverte 2.0. Il regroupe les informations sur les usagers, les véhicules 
                et les caractéristiques des accidents.
              </Text>
              <Link 
                href="https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024" 
                fontWeight="bold"
                color="blue.600"
                display="flex"
                alignItems="center"
                gap={2}
              >
                Accéder au dataset sur data.gouv.fr <LuExternalLink size={16} />
              </Link>
            </VStack>
            
            <Box bg="white" p={6} borderRadius="2xl" boxShadow="sm" minW="250px">
              <VStack align="flex-start" spaceY={2}>
                <Text fontWeight="bold" fontSize="sm" color="gray.500">MÉTHODOLOGIE</Text>
                <Text fontSize="sm">• Nettoyage via Pandas</Text>
                <Text fontSize="sm">• API Django Rest Framework</Text>
                <Text fontSize="sm">• Frontend React & Recharts</Text>
              </VStack>
            </Box>
          </Stack>
        </Box>

      </VStack>
    </Container>
  )
}

function FeatureCard({ icon, title, text }) {
  return (
    <VStack 
      align="flex-start" 
      p={8} 
      borderRadius="2xl" 
      border="1px solid" 
      borderColor="gray.100" 
      transition="all 0.2s"
      _hover={{ transform: "translateY(-5px)", shadow: "md", borderColor: "blue.200" }}
    >
      <Icon as={icon} boxSize={8} color="blue.500" mb={2} />
      <Heading size="md">{title}</Heading>
      <Text color="gray.600" fontSize="sm" lineHeight="tall">
        {text}
      </Text>
    </VStack>
  )
}