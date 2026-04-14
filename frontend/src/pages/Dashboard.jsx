import { Heading, Text, Container } from '@chakra-ui/react'

export default function Dashboard() {
  return (
    <Container maxW="container.xl" py={10}>
      <Heading>Tableau de bord</Heading>
      <Text mt={4}>Ici, nous afficherons les données de l'API Django.</Text>
    </Container>
  )
}