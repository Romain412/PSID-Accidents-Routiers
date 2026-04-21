import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Container, Heading, Text, Flex, Box, SimpleGrid, Icon } from '@chakra-ui/react';
import MarkerClusterGroup from 'react-leaflet-cluster';
import { LuChevronDown } from "react-icons/lu";
import L from 'leaflet';

import SexGravityChart from '../components/charts/SexGravityChart';
import AgeGravityChart from '../components/charts/AgeGravityChart';
import HolidayChart from '../components/charts/HolidayChart';
import VehicleTypeChart from '../components/charts/VehicleTypeChart';

const ANALYSES = {
    "Accidents par sexe et gravité": {
        pourquoi: "Ce graphique croise le sexe et la gravité des blessures pour mettre en évidence des disparités structurelles dans l'exposition au risque routier. Il révèle immédiatement des inégalités de comportement et de vulnérabilité.",
        analyse: "Les hommes représentent une part significativement plus élevée des usagers impliqués. Cette surreprésentation est encore plus marquée dans les catégories les plus graves : la proportion de tués et de blessés hospitalisés est structurellement plus élevée chez les hommes, même à volume total égal. Ce phénomène s'explique par un kilométrage annuel plus élevé, une pratique plus fréquente de la moto (véhicule à fort taux de létalité), et des comportements à risque statistiquement plus répandus.",
        nuance: "Il serait erroné de conclure que les femmes sont de meilleures conductrices. Le différentiel s'explique en grande partie par l'exposition au risque : les hommes conduisent davantage et utilisent plus souvent les modes de transport les plus dangereux. Ce graphique invite à distinguer fréquence d'accident et gravité conditionnelle.",
    },
    "Répartition âge / gravité": {
        pourquoi: "La pyramide des âges croisée avec la gravité permet d'identifier deux types de sur-risque distincts : le risque d'être impliqué dans un accident (fréquence) et le risque de mourir ou d'être gravement blessé une fois impliqué (létalité). Ces deux dimensions ne concernent pas les mêmes populations.",
        analyse: "Les 18-25 ans sont la tranche la plus représentée en volume absolu, portés par l'inexpérience, une forte mobilité et des comportements à risque plus fréquents. À l'inverse, les 65 ans et plus présentent un profil de létalité élevée : bien que moins souvent impliqués, leur proportion de tués et blessés graves parmi les accidentés est significativement plus haute. La fragilité physiologique amplifie les conséquences d'un traumatisme à énergie équivalente.",
        nuance: "Ce graphique illustre la distinction cruciale entre population exposée et population vulnérable — deux cibles différentes pour deux politiques publiques différentes : prévention comportementale pour les jeunes, adaptation de l'environnement routier pour les seniors.",
    },
    "Accidents par saisons": {
        pourquoi: "La saisonnalité permet de tester une intuition commune — les conditions hivernales seraient plus dangereuses — et de la confronter aux données réelles. Ce graphique est analytiquement intéressant précisément parce que le résultat est souvent contre-intuitif.",
        analyse: "Contrairement à l'idée reçue, l'été concentre généralement le plus grand nombre d'accidents corporels. Le trafic est significativement plus dense (départs en vacances, tourisme), l'usage de la moto et du vélo est à son maximum, et les longues journées augmentent l'exposition. L'hiver, malgré des conditions météorologiques plus hostiles, voit un volume moindre d'accidents car le trafic total est plus faible.",
        nuance: "Ce graphique mesure le volume d'accidents, pas le risque par kilomètre parcouru. En normalisant par le trafic réel, l'hiver retrouverait une dangerosité relative plus élevée. L'été a plus d'accidents parce qu'il y a plus de voitures sur les routes, pas nécessairement parce que les conditions y sont intrinsèquement plus risquées.",
    },
    "Proportion des types de véhicules": {
        pourquoi: "Identifier les catégories de véhicules les plus impliquées permet de cibler les politiques de prévention. Ce graphique révèle aussi la structure du parc automobile français et ses angles morts en matière de sécurité.",
        analyse: "Les voitures légères dominent le volume d'accidents, reflet de leur prépondérance dans le parc roulant. Plus intéressante est la surreprésentation des deux et trois-roues motorisés : malgré une part de marché modeste, ils concentrent une fraction disproportionnée des accidents corporels. Ce déséquilibre est encore plus marqué sur la gravité — les motocyclistes ont un taux de létalité par accident plusieurs fois supérieur à celui des automobilistes, en raison de l'absence de carrosserie protectrice.",
        nuance: "Ce graphique pose la question du rapport entre part modale et part accidentelle : un mode sur-représenté dans les accidents par rapport à son usage réel est structurellement plus dangereux. Les deux-roues motorisés et la mobilité douce sont dans cette situation, notamment dans un contexte d'essor des mobilités alternatives en milieu urbain.",
    },
};

function StatCard({ title, children }) {
    const [open, setOpen] = React.useState(false);
    const analysis = ANALYSES[title];

    return (
        <Box 
            bg="white" 
            p={5} 
            borderRadius="xl" 
            boxShadow="md" 
            border="1px solid" 
            borderColor="gray.100"
            transition="all 0.2s"
            _hover={{ borderColor: "blue.200" }}
        >
            <Flex
                align="center"
                justify="space-between"
                cursor="pointer"
                onClick={() => setOpen(o => !o)}
                mb={4}
                role="button"
                aria-expanded={open}
                userSelect="none"
            >
                <Heading size="md" color="gray.700">{title}</Heading>
                
                {/* La flèche agrandie et animée */}
                <Box
                    transition="transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    transform={open ? 'rotate(180deg)' : 'rotate(0deg)'}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                >
                    <Icon 
                        as={LuChevronDown} 
                        boxSize="7" // Taille de l'icône (28px environ)
                        color={open ? "blue.500" : "gray.400"} 
                    />
                </Box>
            </Flex>

            {open && analysis && (
                <Box 
                    mb={5} 
                    p={5} 
                    bg="blue.50" 
                    borderRadius="lg" 
                    borderLeft="4px solid" 
                    borderColor="blue.400" 
                    fontSize="sm"
                    animation="slide-down 0.2s ease-out" // Optionnel : petit effet d'apparition
                >
                    <Text fontWeight="bold" color="blue.800" mb={1} fontSize="xs" textTransform="uppercase" letterSpacing="wider">
                        Pourquoi ce graphique ?
                    </Text>
                    <Text color="gray.700" mb={4} lineHeight="tall">{analysis.pourquoi}</Text>

                    <Text fontWeight="bold" color="blue.800" mb={1} fontSize="xs" textTransform="uppercase" letterSpacing="wider">
                        Ce que les données montrent
                    </Text>
                    <Text color="gray.700" mb={4} lineHeight="tall">{analysis.analyse}</Text>

                    <Text fontWeight="bold" color="blue.800" mb={1} fontSize="xs" textTransform="uppercase" letterSpacing="wider">
                        Nuance analytique
                    </Text>
                    <Text color="gray.700" lineHeight="tall" fontStyle="italic">{analysis.nuance}</Text>
                </Box>
            )}

            {children}
        </Box>
    );
}

export default function Dashboard() {
    const [locations, setLocations] = useState([]);
    const [selectedAccident, setSelectedAccident] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

    useEffect(() => {
        fetch('https://psid-accidents-routiers.onrender.comapi/accidents/locations/')
            .then(res => res.json())
            .then(data => setLocations(data))
            .catch(err => console.error("Erreur de chargement des points :", err));
    }, []);

    const handlePointClick = (num_acc) => {
        setLoadingDetails(true);
        fetch(`https://psid-accidents-routiers.onrender.comapi/accident/${num_acc}/`)
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

    const createCustomClusterIcon = (cluster) => {
        const count = cluster.getChildCount();
        const size = Math.max(20, 15 + (Math.log(count) * 8));
        return L.divIcon({
            html: `<div style="
                background-color: rgba(229, 62, 62, 0.6);
                border: 2px solid #C53030;
                border-radius: 50%;
                width: 100%;
                height: 100%;
                transition: all 0.2s ease-in-out;
            "></div>`,
            className: '',
            iconSize: L.point(size, size, true),
        });
    };

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={2} fontWeight="bold">Tableau de bord des Accidents (2024)</Heading>

            <Heading mb={1} mt={6}>Carte des accidents</Heading>
            <Text color="gray.600">Sélectionnez un point sur la carte pour voir les détails de l'accident.</Text>
            <Text color="gray.400" mb={3} fontSize='xs'>(Le chargement des points peut prendre quelques secondes)</Text>

            <Flex gap={6} h="70vh">
                <Box flex={2} borderRadius="lg" overflow="hidden" boxShadow="md">
                    <MapContainer center={[46.2276, 2.2137]} zoom={6} style={{ height: '100%', width: '100%' }} preferCanvas={true}>
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        />
                        <MarkerClusterGroup chunkedLoading={true} iconCreateFunction={createCustomClusterIcon} showCoverageOnHover={false}>
                            {locations.map(loc => (
                                <CircleMarker
                                    key={loc.id}
                                    center={[loc.lat, loc.long]}
                                    radius={5}
                                    pathOptions={{ color: 'red', fillColor: '#e53e3e', fillOpacity: 0.8 }}
                                    eventHandlers={{ click: () => handlePointClick(loc.id) }}
                                />
                            ))}
                        </MarkerClusterGroup>
                    </MapContainer>
                </Box>

                <Box flex={1} p={6} bg="gray.50" borderRadius="lg" boxShadow="md" overflowY="auto">
                    {loadingDetails && <Text>Chargement des données...</Text>}

                    {!loadingDetails && selectedAccident ? (
                        <Box>
                            <Heading size="md" color="blue.600" mb={4}>
                                Accident N° {selectedAccident.caracteristiques.Num_Acc}
                            </Heading>
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

            <Box borderBottomWidth="2px" borderColor="gray.300" my={5} w="100%" />

            <Heading mb={2}>Analyses statistiques</Heading>
            <Text color="gray.500" fontSize="sm" mb={6}>Cliquez sur le titre d'un graphique pour afficher son analyse.</Text>

            <SimpleGrid columns={{ base: 1, xl: 2 }} spacing={6}>
                <StatCard title="Accidents par sexe et gravité">
                    <SexGravityChart />
                </StatCard>

                <StatCard title="Répartition âge / gravité">
                    <AgeGravityChart />
                </StatCard>

                <StatCard title="Accidents par saisons">
                    <HolidayChart />
                </StatCard>

                <StatCard title="Proportion des types de véhicules">
                    <VehicleTypeChart />
                </StatCard>
            </SimpleGrid>
        </Container>
    );
}
