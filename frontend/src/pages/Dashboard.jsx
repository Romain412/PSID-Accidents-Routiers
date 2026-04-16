import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Container, Heading, Text, Flex, Box, SimpleGrid } from '@chakra-ui/react';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';

/* FUTURS COMPOSANTS DE GRAPHIQUES */
import RainCorrelationChart from '../components/charts/RainCorrelationChart';
import VehicleTypeChart from '../components/charts/VehicleTypeChart';
import AgeAccidentChart from '../components/charts/AgeAccidentChart';
import RoadTypeChart from '../components/charts/RoadTypeChart';
import HolidayChart from '../components/charts/HolidayChart';
import HeatmapChart from '../components/charts/HeatmapChart';


function StatCard({ title, children }) {
    return (
        <Box bg="white" p={5} borderRadius="lg" boxShadow="md">
            <Heading size="md" mb={4}>{title}</Heading>
            {children}
        </Box>
    );
}

export default function Dashboard() {
    const [locations, setLocations] = useState([]);
    const [selectedAccident, setSelectedAccident] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

    // 1. Récupération des coordonnées au chargement
    useEffect(() => {
        fetch('http://localhost:8000/api/accidents/locations/')
            .then(res => res.json())
            .then(data => setLocations(data))
            .catch(err => console.error("Erreur de chargement des points :", err));
    }, []);

    // 2. Récupération des détails au clic
    const handlePointClick = (num_acc) => {
        setLoadingDetails(true);
        fetch(`http://localhost:8000/api/accident/${num_acc}/`)
            .then(res => res.json())
            .then(data => {
                setSelectedAccident(data);
                setLoadingDetails(false);
            })
            .catch(err => {
                console.error("Erreur de chargement des détails :", err);
                setLoadingDetails(false);
            });
    };

    // Fonction magique pour créer des bulles de taille dynamique
    const createCustomClusterIcon = (cluster) => {
        // On récupère le nombre d'accidents dans ce groupe
        const count = cluster.getChildCount();

        // Calcul de la taille de la bulle (minimum 20px, puis grandit avec le nombre)
        const size = Math.max(20, 15 + (Math.log(count) * 8));

        // On retourne un cercle dessiné en pur HTML/CSS
        return L.divIcon({
            html: `<div style="
                background-color: rgba(229, 62, 62, 0.6); /* Rouge Chakra UI (e53e3e) avec transparence */
                border: 2px solid #C53030; /* Bordure rouge plus foncé */
                border-radius: 50%;
                width: 100%;
                height: 100%;
                transition: all 0.2s ease-in-out;
            "></div>`,
            className: '', // Vide pour désactiver le CSS par défaut de MarkerCluster
            iconSize: L.point(size, size, true), // Applique la taille calculée
        });
    };

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={2} fontWeight="bold">Tableau de bord des Accidents (2024)</Heading>

            <Heading mb={1} mt={6}>Carte des accidents</Heading>

            <Text color="gray.600" mb={3}>Sélectionnez un point sur la carte pour voir les détails de l'accident.</Text>

            {/* Flex permet de mettre la carte et les détails côte à côte */}
            <Flex gap={6} h="70vh">

                {/* --- SECTION GAUCHE : LA CARTE --- */}
                <Box flex={2} borderRadius="lg" overflow="hidden" boxShadow="md">
                    <MapContainer center={[46.2276, 2.2137]} zoom={6} style={{ height: '100%', width: '100%' }} preferCanvas={true}>
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        />
                        <MarkerClusterGroup chunkedLoading={true} iconCreateFunction={createCustomClusterIcon} showCoverageOnHover={false} >
                            {locations.map(loc => (
                                <CircleMarker
                                    key={loc.id}
                                    center={[loc.lat, loc.long]}
                                    radius={5}
                                    pathOptions={{ color: 'red', fillColor: '#e53e3e', fillOpacity: 0.8 }}
                                    eventHandlers={{
                                        click: () => handlePointClick(loc.id),
                                    }}
                                />
                            ))}
                        </MarkerClusterGroup>
                    </MapContainer>
                </Box>

                {/* --- SECTION DROITE : LES DÉTAILS --- */}
                {/* --- SECTION DROITE : LES DÉTAILS --- */}
                <Box flex={1} p={6} bg="gray.50" borderRadius="lg" boxShadow="md" overflowY="auto">
                    {loadingDetails && <Text>Chargement des données...</Text>}

                    {!loadingDetails && selectedAccident ? (
                        <Box>
                            <Heading size="md" color="blue.600" mb={4}>
                                Accident N° {selectedAccident.caracteristiques.Num_Acc}
                            </Heading>

                            {/* Notre ligne de séparation sécurisée */}
                            <Box borderBottomWidth="1px" borderColor="gray.300" w="100%" mb={4} />

                            <Box mb={6}>
                                <Text><strong>Date :</strong> {selectedAccident.caracteristiques.date_formatee}</Text>
                                <Text><strong>Heure :</strong> {selectedAccident.caracteristiques.hrmn}</Text>
                                <Text><strong>Département :</strong> {selectedAccident.caracteristiques.dep}</Text>
                                <Text><strong>Adresse :</strong> {selectedAccident.caracteristiques.adr}</Text>
                            </Box>

                            <Heading size="sm" mb={3}>Véhicules impliqués ({selectedAccident.vehicules.length})</Heading>
                            <Box mb={6}>
                                {selectedAccident.vehicules.map(veh => (
                                    <Box key={veh.id_vehicule} p={3} mb={2} bg="white" borderRadius="md" shadow="sm" borderWidth="1px">
                                        <Text>Catégorie : <strong>{veh.catv}</strong></Text>
                                    </Box>
                                ))}
                            </Box>

                            <Heading size="sm" mb={3}>Usagers impliqués ({selectedAccident.usagers.length})</Heading>
                            <Box>
                                {selectedAccident.usagers.map(usa => (
                                    <Box key={usa.id_usager} p={3} mb={2} bg="white" borderRadius="md" shadow="sm" borderWidth="1px">
                                        <Text>
                                            <strong>Sexe :</strong> {usa.sexe} <br />
                                            <strong>Gravité :</strong> {usa.grav}
                                        </Text>
                                    </Box>
                                ))}
                            </Box>
                        </Box>
                    ) : (
                        !loadingDetails && (
                            <Flex h="100%" align="center" justify="center">
                                <Text color="gray.400" fontStyle="italic" textAlign="center">
                                    Cliquez sur un point rouge sur la carte pour afficher les informations de l'accident ici.
                                </Text>
                            </Flex>
                        )
                    )}
                </Box>
            </Flex>

            <Box
                borderBottomWidth="2px"
                borderColor="gray.300"
                my={5}
                w="100%"
            />

            {/* ===================== GRAPHIQUES ===================== */}

            <Heading mb={6}>Analyses statistiques</Heading>

            <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={6}>
                <StatCard title="Corrélation pluie / chaussée / type d'accident">
                    <RainCorrelationChart />
                </StatCard>

                <StatCard title="Proportion des types de véhicules">
                    <VehicleTypeChart />
                </StatCard>

                <StatCard title="Répartition âge / accidents">
                    <AgeAccidentChart />
                </StatCard>

                <StatCard title="Type de routes / accidents">
                    <RoadTypeChart />
                </StatCard>

                <StatCard title="Vacances / accidents">
                    <HolidayChart />
                </StatCard>

                <StatCard title="Zones accidentogènes / Heatmap">
                    <HeatmapChart />
                </StatCard>
            </SimpleGrid>
        </Container>
    );
}