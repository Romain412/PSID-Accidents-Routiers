import React, { useState, useEffect } from 'react';
import {
    Container, Heading, Text, Flex, Box, Spinner, VStack,
} from '@chakra-ui/react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { API_BASE } from '../config';

// ── Règles de cohérence ───────────────────────────────────────────────────────

const CATR_BY_AGG = {
    'En agglomération': [
        'Voie Communales', 'Routes de métropole urbaine',
        'Route Départementale', 'Route nationale',
        'Parc de stationnement ouvert à la circulation publique', 'Autre',
    ],
    'Hors agglomération': [
        'Autoroute', 'Route nationale',
        'Route Départementale', 'Hors réseau public', 'Autre',
    ],
};

// Types de voie qui forcent une zone précise
const CATR_FORCES_AGG = {
    'Autoroute':                                                'Hors agglomération',
    'Routes de métropole urbaine':                              'En agglomération',
    'Voie Communales':                                          'En agglomération',
    'Parc de stationnement ouvert à la circulation publique':   'En agglomération',
};

function getValidVma(catr, agg) {
    if (catr === 'Autoroute')                                               return [110, 130];
    if (catr === 'Parc de stationnement ouvert à la circulation publique')  return [30];
    if (agg === 'En agglomération')                                         return [30, 50, 70];
    if (catr === 'Hors réseau public')                                      return [30, 50, 80];
    return [70, 80, 90];   // Route dép., nationale, Autre hors agglo
}

function snapVma(vma, validVma) {
    if (validVma.includes(vma)) return vma;
    return validVma.reduce((best, v) => Math.abs(v - vma) < Math.abs(best - vma) ? v : best);
}

// ── Données statiques ─────────────────────────────────────────────────────────

const LUM_OPTIONS = [
    'Plein jour', 'Crépuscule ou aube',
    'Nuit avec éclairage public allumé',
    'Nuit avec éclairage public non allumé',
    'Nuit sans éclairage public',
];
const LUM_ABBREV = ['Plein jour', 'Crépuscule', 'Nuit éclairée', 'Nuit non éclairée', 'Nuit sans éclairage'];

const ATM_OPTIONS = [
    'Normale', 'Temps couvert', 'Pluie légère', 'Pluie forte',
    'Vent fort - tempête', 'Brouillard - fumée', 'Neige - grêle', 'Temps éblouissant',
];
const ATM_ABBREV = ['Normale', 'Couvert', 'Pluie légère', 'Pluie forte', 'Tempête', 'Brouillard', 'Neige', 'Éblouissant'];

const MODEL_OPTIONS = [
    { value: 'bisecting_kmeans', label: 'Bisecting K-Means' },
    { value: 'kmeans',           label: 'K-Means' },
    { value: 'gmm',              label: 'Gaussian Mixture Model' },
];

const GRAVITE_COLORS = {
    'Indemne':      '#38A169',
    'Blessé léger': '#D69E2E',
    'Blessé grave': '#DD6B20',
    'Tué':          '#E53E3E',
};

const SELECT_STYLE = {
    height: '40px', padding: '0 10px', borderRadius: '8px',
    border: '1px solid #CBD5E0', fontSize: '14px',
    background: 'white', width: '100%', cursor: 'pointer',
};

const DEFAULT_FORM = {
    lum: 'Plein jour', atm: 'Normale', agg: 'En agglomération',
    catr: 'Voie Communales', vma: 50, model: 'bisecting_kmeans',
};

// ── Composants UI ─────────────────────────────────────────────────────────────

function SliderField({ label, value, options, abbrev, onChange }) {
    const idx     = options.findIndex(o => String(o) === String(value));
    const current = idx === -1 ? 0 : idx;

    return (
        <Box>
            <Flex justify="space-between" align="baseline" mb={2}>
                <Text fontSize="sm" fontWeight="semibold" color="gray.700">{label}</Text>
                <Text fontSize="sm" fontWeight="bold" color="blue.600">
                    {abbrev ? abbrev[current] : String(options[current])}
                    {typeof options[0] === 'number' ? ' km/h' : ''}
                </Text>
            </Flex>
            <input
                type="range" min={0} max={options.length - 1} value={current}
                onChange={e => onChange(options[parseInt(e.target.value)])}
                style={{ width: '100%', accentColor: '#3182CE', height: '6px', cursor: 'pointer' }}
            />
            <Flex justify="space-between" mt={1}>
                {(abbrev || options.map(String)).map((lbl, i) => (
                    <Text key={i} fontSize="9px"
                        color={i === current ? 'blue.500' : 'gray.300'}
                        fontWeight={i === current ? 'bold' : 'normal'}
                        textAlign="center" flex={1} lineHeight="1.2"
                        style={{ wordBreak: 'break-word', maxWidth: `${100 / options.length}%` }}>
                        {typeof options[0] === 'number' ? options[i] : lbl.split(' ')[0]}
                    </Text>
                ))}
            </Flex>
        </Box>
    );
}

function ZoneToggle({ value, onChange }) {
    const isAgglo = value === 'En agglomération';
    return (
        <Box>
            <Text fontSize="sm" fontWeight="semibold" color="gray.700" mb={3}>Zone</Text>
            <Flex align="center" gap={4}>
                <Text fontSize="sm" userSelect="none"
                    color={isAgglo ? 'blue.600' : 'gray.400'}
                    fontWeight={isAgglo ? 'bold' : 'normal'}>
                    En agglomération
                </Text>
                <Box w="52px" h="28px" borderRadius="full" cursor="pointer" flexShrink={0}
                    bg={isAgglo ? 'blue.500' : 'gray.400'}
                    position="relative" transition="background 0.25s"
                    onClick={() => onChange(isAgglo ? 'Hors agglomération' : 'En agglomération')}>
                    <Box position="absolute" top="3px"
                        left={isAgglo ? '3px' : '25px'}
                        w="22px" h="22px" borderRadius="full" bg="white"
                        boxShadow="sm" transition="left 0.25s" />
                </Box>
                <Text fontSize="sm" userSelect="none"
                    color={!isAgglo ? 'blue.600' : 'gray.400'}
                    fontWeight={!isAgglo ? 'bold' : 'normal'}>
                    Hors agglomération
                </Text>
            </Flex>
        </Box>
    );
}

// ── Page principale ────────────────────────────────────────────────────────────

export default function Simulateur() {
    const [departments, setDepartments] = useState([]);
    const [dep,         setDep]         = useState('');
    const [form,        setForm]        = useState(DEFAULT_FORM);
    const [loading,     setLoading]     = useState(false);
    const [error,       setError]       = useState(null);
    const [result,      setResult]      = useState(null);

    useEffect(() => {
        fetch(`${API_BASE}/api/departments/`)
            .then(r => r.json())
            .then(data => { setDepartments(data); if (data.length) setDep(data[0].code); })
            .catch(() => {});
    }, []);

    // Auto-submit avec debounce 400 ms
    useEffect(() => {
        if (!dep) return;
        const timer = setTimeout(async () => {
            setLoading(true); setError(null);
            try {
                const params = new URLSearchParams({
                    dep, model: form.model,
                    lum: form.lum, atm: form.atm, agg: form.agg,
                    catr: form.catr, catv: 'VL seul', vma: String(form.vma),
                });
                const res  = await fetch(`${API_BASE}/api/simulator/?${params}`);
                const data = await res.json();
                if (!res.ok) setError(data.error || 'Erreur.'); else setResult(data);
            } catch { setError('Impossible de contacter le serveur.'); }
            finally { setLoading(false); }
        }, 400);
        return () => clearTimeout(timer);
    }, [dep, form.lum, form.atm, form.agg, form.catr, form.vma, form.model]);

    // ── Setters avec cohérence en cascade ──────────────────────────────────────

    const setAgg = (newAgg) => {
        const validCatr = CATR_BY_AGG[newAgg];
        const newCatr   = validCatr.includes(form.catr) ? form.catr : validCatr[0];
        const validVma  = getValidVma(newCatr, newAgg);
        setForm(f => ({ ...f, agg: newAgg, catr: newCatr, vma: snapVma(f.vma, validVma) }));
    };

    const setCatr = (newCatr) => {
        const newAgg   = CATR_FORCES_AGG[newCatr] ?? form.agg;
        const validVma = getValidVma(newCatr, newAgg);
        setForm(f => ({ ...f, catr: newCatr, agg: newAgg, vma: snapVma(f.vma, validVma) }));
    };

    const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

    // ── Dérivé ─────────────────────────────────────────────────────────────────

    const validCatr = CATR_BY_AGG[form.agg];
    const validVma  = getValidVma(form.catr, form.agg);

    const chartData = result ? [
        { name: 'Indemne',      value: result.pct_indemne },
        { name: 'Blessé léger', value: result.pct_blesse_leger },
        { name: 'Blessé grave', value: result.pct_blesse_grave },
        { name: 'Tué',          value: result.pct_tue },
    ] : [];

    return (
        <Container maxW="container.xl" py={8}>
            <Flex align="baseline" gap={3} mb={1}>
                <Heading fontWeight="bold">Simulateur de risque</Heading>
                {loading && <Spinner size="sm" color="blue.400" />}
            </Flex>
            <Text color="gray.500" mb={6}>
                Ajustez les conditions de conduite — l'estimation se met à jour automatiquement.
            </Text>

            <Flex gap={6} direction={{ base: 'column', lg: 'row' }}>

                {/* Formulaire */}
                <Box flex={1} bg="white" p={6} borderRadius="xl" boxShadow="md"
                    border="1px solid" borderColor="gray.100">

                    <Flex gap={4} mb={6} direction={{ base: 'column', sm: 'row' }}>
                        <Box flex={2}>
                            <Text fontSize="xs" fontWeight="medium" color="gray.500" mb={1}>Département</Text>
                            <select value={dep} onChange={e => setDep(e.target.value)} style={SELECT_STYLE}>
                                {departments.map(d => (
                                    <option key={d.code} value={d.code}>{d.nom} ({d.code})</option>
                                ))}
                            </select>
                        </Box>
                        <Box flex={2}>
                            <Text fontSize="xs" fontWeight="medium" color="gray.500" mb={1}>Modèle</Text>
                            <select value={form.model} onChange={e => set('model', e.target.value)} style={SELECT_STYLE}>
                                {MODEL_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                            </select>
                        </Box>
                    </Flex>

                    <VStack align="stretch" gap={6} divider={<Box h="1px" bg="gray.100" />}>

                        <SliderField label="Luminosité" value={form.lum}
                            options={LUM_OPTIONS} abbrev={LUM_ABBREV}
                            onChange={v => set('lum', v)} />

                        <SliderField label="Conditions météo" value={form.atm}
                            options={ATM_OPTIONS} abbrev={ATM_ABBREV}
                            onChange={v => set('atm', v)} />

                        <ZoneToggle value={form.agg} onChange={setAgg} />

                        {/* Type de voie filtré selon la zone */}
                        <Box>
                            <Text fontSize="xs" fontWeight="medium" color="gray.500" mb={1}>Type de voie</Text>
                            <select value={form.catr} onChange={e => setCatr(e.target.value)} style={SELECT_STYLE}>
                                {validCatr.map(o => <option key={o} value={o}>{o}</option>)}
                            </select>
                        </Box>

                        {/* Vitesse filtrée selon voie + zone */}
                        <SliderField label="Vitesse max autorisée" value={form.vma}
                            options={validVma}
                            onChange={v => set('vma', v)} />

                    </VStack>
                </Box>

                {/* Résultat */}
                <Box flex={1} bg="white" p={6} borderRadius="xl" boxShadow="md"
                    border="1px solid" borderColor="gray.100"
                    display="flex" flexDirection="column" justifyContent="center" minH="400px">

                    {!result && !loading && !error && (
                        <Flex h="100%" align="center" justify="center">
                            <Text color="gray.400" fontStyle="italic">Chargement…</Text>
                        </Flex>
                    )}

                    {error && (
                        <Box p={4} bg="red.50" border="1px solid" borderColor="red.200"
                            borderRadius="lg" color="red.700">{error}</Box>
                    )}

                    {result && (
                        <VStack align="stretch" gap={5}
                            opacity={loading ? 0.5 : 1} transition="opacity 0.2s">

                            <Box>
                                <Text fontSize="xs" fontWeight="bold" color="blue.600"
                                    textTransform="uppercase" letterSpacing="wider" mb={3}>
                                    Contribution des clusters
                                </Text>
                                <VStack align="stretch" gap={2}>
                                    {result.contributions?.map(c => (
                                        <Box key={c.cluster_number}>
                                            <Flex align="center" gap={2} mb="3px">
                                                <Text fontSize="xs" fontWeight="semibold" color="gray.600" minW="64px">
                                                    Cluster {c.cluster_number + 1}
                                                </Text>
                                                <Box flex={1} h="8px" bg="gray.100" borderRadius="full" overflow="hidden">
                                                    <Box h="100%" bg="blue.400" borderRadius="full"
                                                        transition="width 0.3s" style={{ width: `${c.poids}%` }} />
                                                </Box>
                                                <Text fontSize="xs" color="blue.600" fontWeight="bold"
                                                    minW="36px" textAlign="right">{c.poids}%</Text>
                                            </Flex>
                                            {c.profil && (
                                                <Text fontSize="xs" color="gray.400" pl="72px" lineHeight="short">
                                                    {c.profil}
                                                </Text>
                                            )}
                                        </Box>
                                    ))}
                                </VStack>
                            </Box>

                            <Box>
                                <Text fontSize="xs" fontWeight="bold" color="blue.600"
                                    textTransform="uppercase" letterSpacing="wider" mb={3}>
                                    Répartition estimée des blessures
                                </Text>
                                <ResponsiveContainer width="100%" height={200}>
                                    <BarChart data={chartData} layout="vertical"
                                        margin={{ top: 0, right: 55, left: 10, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                        <XAxis type="number" domain={[0, 100]}
                                            tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
                                        <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 12 }} />
                                        <Tooltip formatter={v => [`${v.toFixed(1)}%`, 'Probabilité']} />
                                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                            {chartData.map(entry => (
                                                <Cell key={entry.name} fill={GRAVITE_COLORS[entry.name]} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </Box>

                            <Text fontSize="xs" color="gray.300" pt={1}
                                borderTop="1px solid" borderColor="gray.100">
                                {result.methode === 'predict_proba'
                                    ? 'Estimation par probabilités GMM (predict_proba)'
                                    : 'Estimation par pondération inverse des distances aux centroïdes'}
                            </Text>
                        </VStack>
                    )}
                </Box>
            </Flex>
        </Container>
    );
}
