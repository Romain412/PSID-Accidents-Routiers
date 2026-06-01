import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import {
    Container, Heading, Text, Flex, Box, Input, Button,
    Spinner, Badge, HStack, VStack,
} from '@chakra-ui/react';
import { LuArrowRight, LuRoute } from 'react-icons/lu';
import { API_BASE } from '../config';

function FitBounds({ coords }) {
    const map = useMap();
    useEffect(() => {
        if (coords && coords.length > 0) {
            map.fitBounds(coords.map(c => [c[1], c[0]]), { padding: [40, 40] });
        }
    }, [coords, map]);
    return null;
}

function formatDuration(minutes) {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return h > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${m} min`;
}

export default function Itineraire() {
    const [depart,  setDepart]  = useState('');
    const [arrivee, setArrivee] = useState('');
    const [loading, setLoading] = useState(false);
    const [error,   setError]   = useState(null);
    const [result,  setResult]  = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!depart.trim() || !arrivee.trim()) return;
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const res = await fetch(
                `${API_BASE}/api/route/departments/?depart=${encodeURIComponent(depart)}&arrivee=${encodeURIComponent(arrivee)}`
            );
            const data = await res.json();
            if (!res.ok) {
                setError(data.error || 'Une erreur est survenue.');
            } else {
                setResult(data);
            }
        } catch {
            setError('Impossible de contacter le serveur.');
        } finally {
            setLoading(false);
        }
    };

    const routeLatLngs = result?.route?.map(c => [c[1], c[0]]) ?? [];

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={1} fontWeight="bold">Itinéraire & Départements traversés</Heading>
            <Text color="gray.500" mb={6}>
                Calculez un trajet routier et découvrez les départements français traversés, dans l'ordre de passage.
            </Text>

            {/* Formulaire */}
            <Box
                as="form"
                onSubmit={handleSubmit}
                bg="white"
                p={6}
                borderRadius="xl"
                boxShadow="md"
                border="1px solid"
                borderColor="gray.100"
                mb={6}
            >
                <Flex gap={4} align="flex-end" direction={{ base: 'column', md: 'row' }}>
                    <Box flex={1}>
                        <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>Départ</Text>
                        <Input
                            placeholder="ex. Paris"
                            value={depart}
                            onChange={e => setDepart(e.target.value)}
                            size="lg"
                            required
                        />
                    </Box>
                    <Flex pb={1} color="gray.300" display={{ base: 'none', md: 'flex' }}>
                        <LuArrowRight size={28} />
                    </Flex>
                    <Box flex={1}>
                        <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>Arrivée</Text>
                        <Input
                            placeholder="ex. Marseille"
                            value={arrivee}
                            onChange={e => setArrivee(e.target.value)}
                            size="lg"
                            required
                        />
                    </Box>
                    <Button
                        type="submit"
                        colorPalette="blue"
                        size="lg"
                        loading={loading}
                        loadingText="Calcul en cours..."
                        px={8}
                        minW="200px"
                    >
                        <LuRoute /> Calculer l'itinéraire
                    </Button>
                </Flex>
            </Box>

            {/* Erreur */}
            {error && (
                <Box
                    p={4} mb={6}
                    bg="red.50" border="1px solid" borderColor="red.200"
                    borderRadius="lg" color="red.700"
                >
                    {error}
                </Box>
            )}

            {/* Chargement */}
            {loading && (
                <Flex justify="center" align="center" direction="column" gap={4} py={16}>
                    <Spinner size="xl" color="blue.500" />
                    <Text color="gray.500">Calcul de l'itinéraire en cours…</Text>
                </Flex>
            )}

            {/* Résultats */}
            {result && !loading && (
                <>
                    {/* Bandeau de stats */}
                    <HStack
                        gap={8} mb={5} p={5}
                        bg="blue.50" borderRadius="xl"
                        border="1px solid" borderColor="blue.100"
                    >
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Distance</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{result.distance_km} km</Text>
                        </Box>
                        <Box w="1px" h="40px" bg="blue.200" />
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Durée estimée</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{formatDuration(result.duration_min)}</Text>
                        </Box>
                        <Box w="1px" h="40px" bg="blue.200" />
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Départements traversés</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{result.departements.length}</Text>
                        </Box>
                    </HStack>

                    <Flex gap={6} h="65vh">
                        {/* Carte */}
                        <Box flex={2} borderRadius="lg" overflow="hidden" boxShadow="md">
                            <MapContainer
                                center={[46.2276, 2.2137]}
                                zoom={6}
                                style={{ height: '100%', width: '100%' }}
                            >
                                <TileLayer
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                                />
                                <FitBounds coords={result.route} />
                                <Polyline
                                    positions={routeLatLngs}
                                    pathOptions={{ color: '#3182CE', weight: 5, opacity: 0.85 }}
                                />
                                {/* Marqueur départ (vert) */}
                                <CircleMarker
                                    center={[result.depart.lat, result.depart.lon]}
                                    radius={9}
                                    pathOptions={{ color: '#15803D', fillColor: '#22C55E', fillOpacity: 1, weight: 2 }}
                                />
                                {/* Marqueur arrivée (rouge) */}
                                <CircleMarker
                                    center={[result.arrivee.lat, result.arrivee.lon]}
                                    radius={9}
                                    pathOptions={{ color: '#B91C1C', fillColor: '#EF4444', fillOpacity: 1, weight: 2 }}
                                />
                            </MapContainer>
                        </Box>

                        {/* Liste des départements */}
                        <Box flex={1} bg="gray.50" borderRadius="lg" boxShadow="md" overflowY="auto" p={5}>
                            <Text
                                fontWeight="bold" color="gray.600" mb={4}
                                fontSize="xs" textTransform="uppercase" letterSpacing="wider"
                            >
                                Ordre de passage
                            </Text>
                            <VStack align="stretch" gap={2}>
                                {result.departements.map((dept, idx) => (
                                    <Flex
                                        key={dept.code}
                                        align="center" gap={3} p={3}
                                        bg="white" borderRadius="md"
                                        boxShadow="sm" border="1px solid" borderColor="gray.100"
                                    >
                                        <Badge
                                            colorPalette="blue"
                                            variant="solid"
                                            minW="28px"
                                            textAlign="center"
                                        >
                                            {idx + 1}
                                        </Badge>
                                        <Box>
                                            <Text fontWeight="semibold" fontSize="sm" color="gray.800">
                                                {dept.nom}
                                            </Text>
                                            <Text fontSize="xs" color="gray.400">
                                                Dép. {dept.code}
                                            </Text>
                                        </Box>
                                    </Flex>
                                ))}
                            </VStack>
                        </Box>
                    </Flex>
                </>
            )}
        </Container>
    );
}
