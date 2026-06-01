import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import {
    Container, Heading, Text, Flex, Box, Input, Button,
    Spinner, Badge, HStack, VStack, Separator,
} from '@chakra-ui/react';
import { LuArrowRight, LuRoute } from 'react-icons/lu';
import { API_BASE } from '../config';

const CLUSTER_COLORS = [
    '#E53E3E', '#3182CE', '#38A169', '#D69E2E',
    '#805AD5', '#DD6B20', '#2B6CB0', '#276749',
];

const MODEL_LABELS = {
    kmeans:           'K-Means',
    bisecting_kmeans: 'Bisecting K-Means',
    gmm:              'Gaussian Mixture Model',
};

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
    const [model,   setModel]   = useState('kmeans');
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
                `${API_BASE}/api/route/departments/?depart=${encodeURIComponent(depart)}&arrivee=${encodeURIComponent(arrivee)}&model=${model}`
            );
            const data = await res.json();
            if (!res.ok) setError(data.error || 'Une erreur est survenue.');
            else setResult(data);
        } catch {
            setError('Impossible de contacter le serveur.');
        } finally {
            setLoading(false);
        }
    };

    const routeLatLngs = result?.route?.map(c => [c[1], c[0]]) ?? [];

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={1} fontWeight="bold">Itinéraire & Clustering des accidents</Heading>
            <Text color="gray.500" mb={6}>
                Calculez un trajet, choisissez un modèle de clustering et visualisez la répartition
                des accidents dans les départements traversés.
            </Text>

            <Box
                as="form"
                onSubmit={handleSubmit}
                bg="white" p={6}
                borderRadius="xl" boxShadow="md"
                border="1px solid" borderColor="gray.100"
                mb={6}
            >
                <Flex gap={4} align="flex-end" direction={{ base: 'column', md: 'row' }}>
                    <Box flex={1}>
                        <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>Départ</Text>
                        <Input
                            placeholder="ex. Paris"
                            value={depart}
                            onChange={e => setDepart(e.target.value)}
                            size="lg" required
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
                            size="lg" required
                        />
                    </Box>

                    <Box minW={{ base: '100%', md: '220px' }}>
                        <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>Modèle de clustering</Text>
                        <select
                            value={model}
                            onChange={e => setModel(e.target.value)}
                            style={{
                                height: '48px',
                                padding: '0 12px',
                                borderRadius: '8px',
                                border: '1px solid #CBD5E0',
                                fontSize: '16px',
                                background: 'white',
                                width: '100%',
                                cursor: 'pointer',
                            }}
                        >
                            <option value="kmeans">K-Means</option>
                            <option value="bisecting_kmeans">Bisecting K-Means</option>
                            <option value="gmm">Gaussian Mixture Model</option>
                        </select>
                    </Box>

                    <Button
                        type="submit"
                        colorPalette="blue"
                        size="lg"
                        loading={loading}
                        loadingText="Calcul en cours..."
                        px={8}
                    >
                        <LuRoute /> Calculer
                    </Button>
                </Flex>
            </Box>

            {error && (
                <Box p={4} mb={6} bg="red.50" border="1px solid" borderColor="red.200"
                    borderRadius="lg" color="red.700">
                    {error}
                </Box>
            )}

            {loading && (
                <Flex justify="center" align="center" direction="column" gap={4} py={16}>
                    <Spinner size="xl" color="blue.500" />
                    <Text color="gray.500">Calcul de l'itinéraire et clustering en cours…</Text>
                </Flex>
            )}

            {result && !loading && (
                <Box>
                    <HStack gap={8} mb={5} p={5} bg="blue.50" borderRadius="xl"
                        border="1px solid" borderColor="blue.100" flexWrap="wrap">
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Distance</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{result.distance_km} km</Text>
                        </Box>
                        <Box w="1px" h="40px" bg="blue.200" display={{ base: 'none', sm: 'block' }} />
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Durée estimée</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{formatDuration(result.duration_min)}</Text>
                        </Box>
                        <Box w="1px" h="40px" bg="blue.200" display={{ base: 'none', sm: 'block' }} />
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Départements</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{result.departements.length}</Text>
                        </Box>
                        <Box w="1px" h="40px" bg="blue.200" display={{ base: 'none', sm: 'block' }} />
                        <Box>
                            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wider">Accidents analysés</Text>
                            <Text fontWeight="bold" fontSize="2xl" color="blue.700">{result.total_accidents}</Text>
                        </Box>
                    </HStack>

                    <Flex gap={6} h="65vh">
                        <Box flex={2} borderRadius="lg" overflow="hidden" boxShadow="md">
                            <MapContainer
                                center={[46.2276, 2.2137]}
                                zoom={6}
                                style={{ height: '100%', width: '100%' }}
                                preferCanvas={true}
                            >
                                <TileLayer
                                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                                />
                                <FitBounds coords={result.route} />
                                {result.clusters.map(cluster =>
                                    cluster.points.map((pt, idx) => (
                                        <CircleMarker
                                            key={`c${cluster.id}-${idx}`}
                                            center={[pt[0], pt[1]]}
                                            radius={4}
                                            pathOptions={{
                                                color:       CLUSTER_COLORS[cluster.id % CLUSTER_COLORS.length],
                                                fillColor:   CLUSTER_COLORS[cluster.id % CLUSTER_COLORS.length],
                                                fillOpacity: 0.65,
                                                weight:      0,
                                            }}
                                        />
                                    ))
                                )}
                                <Polyline
                                    positions={routeLatLngs}
                                    pathOptions={{ color: '#1A202C', weight: 4, opacity: 0.85 }}
                                />
                                <CircleMarker
                                    center={[result.depart.lat, result.depart.lon]}
                                    radius={9}
                                    pathOptions={{ color: '#15803D', fillColor: '#22C55E', fillOpacity: 1, weight: 2 }}
                                />
                                <CircleMarker
                                    center={[result.arrivee.lat, result.arrivee.lon]}
                                    radius={9}
                                    pathOptions={{ color: '#B91C1C', fillColor: '#EF4444', fillOpacity: 1, weight: 2 }}
                                />
                            </MapContainer>
                        </Box>

                        <Box flex={1} bg="gray.50" borderRadius="lg" boxShadow="md" overflowY="auto" p={5}>
                            <Text fontWeight="bold" color="gray.600" mb={3}
                                fontSize="xs" textTransform="uppercase" letterSpacing="wider">
                                Clusters — {MODEL_LABELS[result.model]}
                            </Text>
                            <VStack align="stretch" gap={2} mb={5}>
                                {result.clusters.map(cluster => (
                                    <Flex key={cluster.id} align="center" gap={3} p={3}
                                        bg="white" borderRadius="md" boxShadow="sm"
                                        border="1px solid" borderColor="gray.100">
                                        <Box
                                            w="14px" h="14px" borderRadius="full" flexShrink={0}
                                            bg={CLUSTER_COLORS[cluster.id % CLUSTER_COLORS.length]}
                                        />
                                        <Box>
                                            <Text fontWeight="semibold" fontSize="sm" color="gray.800">
                                                Cluster {cluster.id + 1}
                                            </Text>
                                            <Text fontSize="xs" color="gray.400">
                                                {cluster.count} accident{cluster.count > 1 ? 's' : ''}
                                            </Text>
                                        </Box>
                                    </Flex>
                                ))}
                            </VStack>

                            <Separator mb={4} />

                            <Text fontWeight="bold" color="gray.600" mb={3}
                                fontSize="xs" textTransform="uppercase" letterSpacing="wider">
                                Départements traversés
                            </Text>
                            <VStack align="stretch" gap={2}>
                                {result.departements.map((dept, idx) => (
                                    <Flex key={dept.code} align="center" gap={3} p={3}
                                        bg="white" borderRadius="md" boxShadow="sm"
                                        border="1px solid" borderColor="gray.100">
                                        <Badge colorPalette="blue" variant="solid"
                                            minW="28px" textAlign="center">
                                            {idx + 1}
                                        </Badge>
                                        <Box>
                                            <Text fontWeight="semibold" fontSize="sm" color="gray.800">{dept.nom}</Text>
                                            <Text fontSize="xs" color="gray.400">Dép. {dept.code}</Text>
                                        </Box>
                                    </Flex>
                                ))}
                            </VStack>
                        </Box>
                    </Flex>

                </Box>
            )}
        </Container>
    );
}
