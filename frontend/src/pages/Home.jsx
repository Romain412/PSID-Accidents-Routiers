import { Heading, Text, Container } from '@chakra-ui/react'

export default function Home() {
  return (
    <Container maxW="container.md" py={10}>
      <Heading>Bienvenue sur mon projet</Heading>
      <Text mt={4}>Ceci est la page d'accueil.</Text>
    </Container>
  )
}