import React from 'react';
import { Box, Flex, Text, Link, Separator, HStack, VStack } from '@chakra-ui/react';


const GithubIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
);

const DataIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 4.24 2 7v10c0 2.76 4.48 5 10 5s10-2.24 10-5V7c0-2.76-4.48-5-10-5zm0 2c4.42 0 8 1.79 8 4s-3.58 4-8 4-8-1.79-8-4 3.58-4 8-4zm0 16c-4.42 0-8-1.79-8-4v-2.23C5.61 15.21 8.65 16 12 16s6.39-.79 8-2.23V16c0 2.21-3.58 4-8 4zm0-6c-4.42 0-8-1.79-8-4V8.77C5.61 10.21 8.65 11 12 11s6.39-.79 8-2.23V10c0 2.21-3.58 4-8 4z"/>
    </svg>
);

const PersonIcon = () => (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
    </svg>
);

// ── Composant principal ───────────────────────────────────────────────────────

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <Box
            as="footer"
            bg="gray.50"
            color="gray.500"
            mt="auto"
            pt={10}
            pb={6}
            px={{ base: 6, md: 12 }}
            borderTop="3px solid"
            borderColor="blue.500"
        >
            {/* ── Grille principale ── */}
            <Flex
                direction={{ base: 'column', md: 'row' }}
                justify="space-between"
                align={{ base: 'flex-start', md: 'flex-start' }}
                gap={10}
                maxW="1200px"
                mx="auto"
                mb={8}
            >

                {/* Colonne 1 — Identité projet */}
                <VStack align="flex-start" gap={3} flex={1}>
                    <HStack gap={2}>
                        <Box color="blue.600" fontSize="20px">🚗</Box>
                        <Text
                            fontWeight="800"
                            fontSize="lg"
                            color="gray.800"
                            letterSpacing="tight"
                        >
                            Accidents Routiers
                        </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.400" maxW="260px" lineHeight="1.7">
                        Dashboard d'analyse des accidents corporels de la circulation
                        routière en France — données BAAC 2024.
                    </Text>
                    <Link
                        href="https://github.com/Romain412/PSID-Accidents-Routiers"
                        target="_blank"
                        rel="noopener noreferrer"
                        display="flex"
                        alignItems="center"
                        gap={2}
                        mt={1}
                        px={4}
                        py={2}
                        borderRadius="md"
                        border="1px solid"
                        borderColor="gray.300"
                        color="gray.500"
                        fontSize="sm"
                        fontWeight="500"
                        _hover={{
                            borderColor: 'blue.400',
                            color: 'blue.700',
                            bg: 'blue.50',
                            textDecoration: 'none',
                        }}
                        transition="all 0.2s"
                        style={{ width: 'fit-content' }}
                    >
                        <GithubIcon />
                        Voir sur GitHub
                    </Link>
                </VStack>

                {/* Colonne 2 — Équipe */}
                <VStack align="flex-start" gap={3} flex={1}>
                    <Text
                        fontSize="xs"
                        fontWeight="700"
                        color="blue.600"
                        textTransform="uppercase"
                        letterSpacing="widest"
                    >
                        Équipe
                    </Text>
                    {[
                        { name: 'Kevin SOARES', role: 'Développement & Data' },
                        { name: 'Romain THOMAS', role: 'Développement & Data' },
                    ].map(member => (
                        <HStack key={member.name} gap={3} align="flex-start">
                            <Box color="gray.400" mt="2px">
                                <PersonIcon />
                            </Box>
                            <Box>
                                <Text fontSize="sm" fontWeight="600" color="gray.800">
                                    {member.name}
                                </Text>
                                <Text fontSize="xs" color="gray.400">
                                    {member.role}
                                </Text>
                            </Box>
                        </HStack>
                    ))}
                </VStack>

                {/* Colonne 3 — Dataset & liens */}
                <VStack align="flex-start" gap={3} flex={1}>
                    <Text
                        fontSize="xs"
                        fontWeight="700"
                        color="blue.600"
                        textTransform="uppercase"
                        letterSpacing="widest"
                    >
                        Source des données
                    </Text>
                    <HStack gap={2} align="flex-start">
                        <Box color="gray.400" mt="3px">
                            <DataIcon />
                        </Box>
                        <VStack align="flex-start" gap={0}>
                            <Link
                                href="https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024"
                                target="_blank"
                                rel="noopener noreferrer"
                                fontSize="sm"
                                color="gray.500"
                                _hover={{ color: 'blue.700', textDecoration: 'underline' }}
                            >
                                BAAC 2024 — data.gouv.fr
                            </Link>
                            <Text fontSize="xs" color="gray.400">
                                Ministère de l'Intérieur · ONISR
                            </Text>
                        </VStack>
                    </HStack>
                    <Box
                        px={3}
                        py={1}
                        bg="blue.50"
                        borderRadius="sm"
                        border="1px solid"
                        borderColor="gray.200"
                    >
                        <Text fontSize="xs" color="gray.400">
                            Licence Ouverte / Open Licence 2.0
                        </Text>
                    </Box>

                    <Text
                        fontSize="xs"
                        fontWeight="700"
                        color="blue.600"
                        textTransform="uppercase"
                        letterSpacing="widest"
                        mt={2}
                    >
                        Cours
                    </Text>
                    <Text fontSize="sm" color="gray.400">
                        Projet SI et Données (PSID)
                    </Text>
                    <Text fontSize="xs" color="gray.400">
                        Année 2025 / 2026
                    </Text>
                </VStack>

            </Flex>

            {/* ── Séparateur ── */}
            <Box maxW="1200px" mx="auto">
                <Separator borderColor="gray.200" mb={5} />

                {/* ── Barre de bas de page ── */}
                <Flex
                    direction={{ base: 'column', sm: 'row' }}
                    justify="space-between"
                    align="center"
                    gap={3}
                >
                    <Text fontSize="xs" color="gray.500">
                        © {currentYear} Kevin SOARES & Romain THOMAS — Projet PSID
                    </Text>
                    <HStack gap={4}>
                        <Link
                            href="https://psid-accidents-routiers-front.onrender.com/"
                            target="_blank"
                            rel="noopener noreferrer"
                            fontSize="xs"
                            color="gray.400"
                            _hover={{ color: 'gray.600' }}
                        >
                            Application déployée ↗
                        </Link>
                        <Link
                            href="https://github.com/Romain412/PSID-Accidents-Routiers"
                            target="_blank"
                            rel="noopener noreferrer"
                            fontSize="xs"
                            color="gray.500"
                            _hover={{ color: 'blue.600' }}
                        >
                            GitHub ↗
                        </Link>
                    </HStack>
                </Flex>
            </Box>
        </Box>
    );
}
