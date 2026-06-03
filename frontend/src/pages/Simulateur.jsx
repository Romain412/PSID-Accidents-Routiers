import React, { useState, useEffect, useRef } from 'react';
import {
    Container, Heading, Text, Flex, Box, VStack, Icon,
} from '@chakra-ui/react';
import {
    LuSun, LuCloud, LuMapPin, LuRoute, LuGauge,
} from 'react-icons/lu';
import { API_BASE } from '../config';

// ── Cohérence ─────────────────────────────────────────────────────────────────

const CATR_BY_AGG = {
    'En agglomération':   ['Voie Communales', 'Routes de métropole urbaine', 'Route Départementale', 'Route nationale', 'Parc de stationnement ouvert à la circulation publique', 'Autre'],
    'Hors agglomération': ['Autoroute', 'Route nationale', 'Route Départementale', 'Hors réseau public', 'Autre'],
};
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
    return [70, 80, 90];
}
function snapVma(vma, valid) {
    return valid.includes(vma) ? vma : valid.reduce((b, v) => Math.abs(v - vma) < Math.abs(b - vma) ? v : b);
}

// ── Données ───────────────────────────────────────────────────────────────────

const LUM_OPTIONS = ['Plein jour', 'Crépuscule ou aube', 'Nuit avec éclairage public allumé', 'Nuit avec éclairage public non allumé', 'Nuit sans éclairage public'];
const LUM_ABBREV  = ['Plein jour', 'Crépuscule', 'Nuit éclairée', 'Nuit non éclairée', 'Nuit sans éclairage'];
const ATM_OPTIONS = ['Normale', 'Temps couvert', 'Pluie légère', 'Pluie forte', 'Vent fort - tempête', 'Brouillard - fumée', 'Neige - grêle', 'Temps éblouissant'];
const ATM_ABBREV  = ['Normale', 'Couvert', 'Pluie légère', 'Pluie forte', 'Tempête', 'Brouillard', 'Neige', 'Éblouissant'];

const GRAVITE = [
    { key: 'pct_indemne',      label: 'Indemne',      color: '#38A169', bg: '#F0FFF4', border: '#38A169' },
    { key: 'pct_blesse_leger', label: 'Blessé léger', color: '#D69E2E', bg: '#FFFBEB', border: '#D69E2E' },
    { key: 'pct_blesse_grave', label: 'Blessé grave', color: '#DD6B20', bg: '#FFF5E4', border: '#DD6B20' },
    { key: 'pct_tue',          label: 'Tué',           color: '#E53E3E', bg: '#FFF5F5', border: '#E53E3E' },
];

const DANGER_LEVELS = [
    { max: 5,   color: '#38A169', label: 'Risque faible' },
    { max: 15,  color: '#D69E2E', label: 'Risque modéré' },
    { max: 25,  color: '#DD6B20', label: 'Risque élevé' },
    { max: 100, color: '#E53E3E', label: 'Risque critique' },
];

function getDangerLevel(pct) {
    return DANGER_LEVELS.find(l => pct <= l.max) ?? DANGER_LEVELS.at(-1);
}

const SELECT_STYLE = {
    height: '40px', padding: '0 10px', borderRadius: '8px',
    border: '1px solid #CBD5E0', fontSize: '14px',
    background: 'white', width: '100%', cursor: 'pointer',
};

const DEFAULT_FORM = {
    lum: 'Plein jour', atm: 'Normale', agg: 'En agglomération',
    catr: 'Voie Communales', vma: 50,
};

// ── Hook animation ────────────────────────────────────────────────────────────

function useAnimatedValue(target, duration = 450) {
    const [val,  setVal]  = useState(target);
    const frameRef        = useRef();
    const fromRef         = useRef(target);
    const startRef        = useRef(null);

    useEffect(() => {
        if (frameRef.current) cancelAnimationFrame(frameRef.current);
        const from = fromRef.current;
        startRef.current = null;
        const step = (ts) => {
            if (!startRef.current) startRef.current = ts;
            const p = Math.min((ts - startRef.current) / duration, 1);
            const e = 1 - Math.pow(1 - p, 3);
            setVal(from + (target - from) * e);
            if (p < 1) frameRef.current = requestAnimationFrame(step);
            else fromRef.current = target;
        };
        frameRef.current = requestAnimationFrame(step);
        return () => cancelAnimationFrame(frameRef.current);
    }, [target]);

    return val;
}

// ── Composants ────────────────────────────────────────────────────────────────

function SliderField({ label, icon, value, options, abbrev, onChange }) {
    const idx = options.findIndex(o => String(o) === String(value));
    const cur = idx === -1 ? 0 : idx;
    const isNum = typeof options[0] === 'number';
    return (
        <Box>
            <Flex align="center" justify="space-between" mb={2}>
                <Flex align="center" gap={2}>
                    {icon && <Icon as={icon} color="blue.400" boxSize="15px" />}
                    <Text fontSize="sm" fontWeight="semibold" color="gray.700">{label}</Text>
                </Flex>
                <Text fontSize="sm" fontWeight="bold" color="blue.600">
                    {abbrev ? abbrev[cur] : String(options[cur])}{isNum ? ' km/h' : ''}
                </Text>
            </Flex>
            <input type="range" min={0} max={options.length - 1} value={cur}
                onChange={e => onChange(options[parseInt(e.target.value)])}
                style={{ width: '100%', accentColor: '#3182CE', cursor: 'pointer' }} />
            <Flex justify="space-between" mt={1}>
                {(abbrev ?? options.map(String)).map((lbl, i) => (
                    <Text key={i} fontSize="9px" textAlign="center" flex={1}
                        color={i === cur ? 'blue.500' : 'gray.300'}
                        fontWeight={i === cur ? 'bold' : 'normal'}
                        style={{ maxWidth: `${100 / options.length}%`, wordBreak: 'break-word' }}>
                        {isNum ? options[i] : lbl.split(' ')[0]}
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
            <Flex align="center" gap={2} mb={3}>
                <Icon as={LuMapPin} color="blue.400" boxSize="15px" />
                <Text fontSize="sm" fontWeight="semibold" color="gray.700">Zone</Text>
            </Flex>
            <Flex align="center" gap={4}>
                <Text fontSize="sm" userSelect="none"
                    color={isAgglo ? 'blue.600' : 'gray.400'} fontWeight={isAgglo ? 'bold' : 'normal'}>
                    En agglomération
                </Text>
                <Box w="52px" h="28px" borderRadius="full" cursor="pointer" flexShrink={0}
                    bg={isAgglo ? 'blue.500' : 'gray.400'} position="relative" transition="background 0.25s"
                    onClick={() => onChange(isAgglo ? 'Hors agglomération' : 'En agglomération')}>
                    <Box position="absolute" top="3px" left={isAgglo ? '3px' : '25px'}
                        w="22px" h="22px" borderRadius="full" bg="white"
                        boxShadow="sm" transition="left 0.25s" />
                </Box>
                <Text fontSize="sm" userSelect="none"
                    color={!isAgglo ? 'blue.600' : 'gray.400'} fontWeight={!isAgglo ? 'bold' : 'normal'}>
                    Hors agglomération
                </Text>
            </Flex>
        </Box>
    );
}

function RiskGauge({ dangerPct }) {
    const animated = useAnimatedValue(dangerPct);
    const level    = getDangerLevel(animated);
    const R        = 68;
    const ARC      = Math.PI * R;
    const offset   = ARC * (1 - Math.min(animated, 100) / 100);

    return (
        <Box textAlign="center">
            <Text fontSize="xs" fontWeight="bold" color="gray.500"
                textTransform="uppercase" letterSpacing="wider" mb={2}>
                Risque d'accident grave
            </Text>
            <Box position="relative" display="inline-block">
                <svg width="180" height="100" viewBox="0 0 180 100">
                    <path d={`M 12 88 A ${R} ${R} 0 0 1 168 88`}
                        stroke="#EDF2F7" strokeWidth="14" fill="none" strokeLinecap="round" />
                    <path d={`M 12 88 A ${R} ${R} 0 0 1 168 88`}
                        stroke={level.color} strokeWidth="14" fill="none" strokeLinecap="round"
                        strokeDasharray={ARC} strokeDashoffset={offset}
                        style={{ transition: 'stroke-dashoffset 0.45s cubic-bezier(0.4,0,0.2,1), stroke 0.3s' }} />
                </svg>
                <Box position="absolute" bottom="8px" left="50%"
                    style={{ transform: 'translateX(-50%)' }}>
                    <Text fontSize="3xl" fontWeight="black" lineHeight="1"
                        style={{ color: level.color, transition: 'color 0.3s' }}>
                        {animated.toFixed(1)}%
                    </Text>
                    <Text fontSize="xs" color="gray.500" fontWeight="medium"
                        style={{ color: level.color, transition: 'color 0.3s' }}>
                        {level.label}
                    </Text>
                </Box>
            </Box>
        </Box>
    );
}

function OutcomeCard({ label, pct, color, bg, border }) {
    const animated = useAnimatedValue(pct);
    return (
        <Box flex={1} p={4} borderRadius="xl" textAlign="center"
            style={{ background: bg, borderTop: `4px solid ${border}` }}
            border="1px solid" borderColor="gray.100">
            <Text fontSize="2xl" fontWeight="black" lineHeight="1"
                style={{ color, transition: 'color 0.3s' }}>
                {animated.toFixed(1)}%
            </Text>
            <Text fontSize="xs" color="gray.600" mt={1} fontWeight="semibold"
                textTransform="uppercase" letterSpacing="wider">
                {label}
            </Text>
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

    useEffect(() => {
        if (!dep) return;
        const timer = setTimeout(async () => {
            setLoading(true); setError(null);
            try {
                const params = new URLSearchParams({
                    dep,
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
    }, [dep, form.lum, form.atm, form.agg, form.catr, form.vma]);

    const setAgg = (newAgg) => {
        const validC = CATR_BY_AGG[newAgg];
        const newC   = validC.includes(form.catr) ? form.catr : validC[0];
        const validV = getValidVma(newC, newAgg);
        setForm(f => ({ ...f, agg: newAgg, catr: newC, vma: snapVma(f.vma, validV) }));
    };
    const setCatr = (newCatr) => {
        const newAgg = CATR_FORCES_AGG[newCatr] ?? form.agg;
        const validV = getValidVma(newCatr, newAgg);
        setForm(f => ({ ...f, catr: newCatr, agg: newAgg, vma: snapVma(f.vma, validV) }));
    };
    const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

    const validCatr  = CATR_BY_AGG[form.agg];
    const validVma   = getValidVma(form.catr, form.agg);
    const dangerPct  = result ? result.pct_blesse_grave + result.pct_tue : 0;

    return (
        <Container maxW="container.xl" py={8}>
            <Flex align="center" gap={3} mb={1}>
                <Heading fontWeight="bold">Simulateur de risque</Heading>
                {loading && (
                    <Box w="8px" h="8px" borderRadius="full" bg="blue.400"
                        style={{ animation: 'pulse 1s infinite' }} />
                )}
            </Flex>
            <Text color="gray.500" mb={6}>
                Ajustez les conditions — l'estimation se met à jour automatiquement.
            </Text>

            <Flex gap={6} direction={{ base: 'column', lg: 'row' }}>

                {/* ── Formulaire ── */}
                <Box flex={1} bg="white" p={6} borderRadius="xl" boxShadow="md"
                    border="1px solid" borderColor="gray.100">

                    <Box mb={6}>
                        <Text fontSize="xs" fontWeight="medium" color="gray.500" mb={1}>Département</Text>
                        <select value={dep} onChange={e => setDep(e.target.value)} style={SELECT_STYLE}>
                            {departments.map(d => <option key={d.code} value={d.code}>{d.nom} ({d.code})</option>)}
                        </select>
                    </Box>

                    <VStack align="stretch" gap={6} divider={<Box h="1px" bg="gray.100" />}>
                        <SliderField icon={LuSun}   label="Luminosité"        value={form.lum} options={LUM_OPTIONS} abbrev={LUM_ABBREV} onChange={v => set('lum', v)} />
                        <SliderField icon={LuCloud} label="Conditions météo"  value={form.atm} options={ATM_OPTIONS} abbrev={ATM_ABBREV} onChange={v => set('atm', v)} />
                        <ZoneToggle value={form.agg} onChange={setAgg} />
                        <Box>
                            <Flex align="center" gap={2} mb={2}>
                                <Icon as={LuRoute} color="blue.400" boxSize="15px" />
                                <Text fontSize="sm" fontWeight="semibold" color="gray.700">Type de voie</Text>
                            </Flex>
                            <select value={form.catr} onChange={e => setCatr(e.target.value)} style={SELECT_STYLE}>
                                {validCatr.map(o => <option key={o} value={o}>{o}</option>)}
                            </select>
                        </Box>
                        <SliderField icon={LuGauge} label="Vitesse max autorisée" value={form.vma} options={validVma} onChange={v => set('vma', v)} />
                    </VStack>
                </Box>

                {/* ── Résultat ── */}
                <Box flex={1} bg="white" p={6} borderRadius="xl" boxShadow="md"
                    border="1px solid" borderColor="gray.100" minH="420px">

                    {!result && !error && (
                        <Flex h="100%" align="center" justify="center">
                            <Text color="gray.400" fontStyle="italic">Chargement…</Text>
                        </Flex>
                    )}

                    {error && (
                        <Box p={4} bg="red.50" border="1px solid" borderColor="red.200"
                            borderRadius="lg" color="red.700">{error}</Box>
                    )}

                    {result && (
                        <VStack align="stretch" gap={6}
                            opacity={loading ? 0.6 : 1} transition="opacity 0.2s">

                            {/* Jauge */}
                            <RiskGauge dangerPct={dangerPct} />

                            {/* 4 cartes */}
                            <Flex gap={3} wrap="wrap">
                                {GRAVITE.map(g => (
                                    <OutcomeCard key={g.key} label={g.label}
                                        pct={result[g.key]} color={g.color}
                                        bg={g.bg} border={g.border} />
                                ))}
                            </Flex>

                        </VStack>
                    )}
                </Box>
            </Flex>
        </Container>
    );
}
