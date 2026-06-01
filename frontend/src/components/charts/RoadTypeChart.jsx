// TODO : ce composant est actuellement inutilisé (non importé dans Dashboard.jsx).
// Problème 1 — endpoint manquant : appelle /api/stats/road-types/ qui n'existe ni dans
//   views.py ni dans urls.py. Il faut créer la vue et l'enregistrer dans urls.py.
// Problème 2 — mapping incorrect : ROAD_LABELS traduit des codes numériques (1, 2…),
//   mais en base les valeurs sont déjà en libellés texte (ex. "Autoroute") grâce à
//   import_csv.py. Il faudra utiliser directement le libellé comme dataKey au lieu de
//   passer par ce dictionnaire de codes.
// Une fois ces deux points réglés, importer et ajouter le composant dans Dashboard.jsx.
import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { API_BASE } from '../../config';

const ROAD_LABELS = {
    1: "Autoroute",
    2: "Route nationale",
    3: "Route Départementale",
    4: "Voie Communale",
    5: "Hors réseau public",
    6: "Parking public",
    7: "Métropole urbaine",
    9: "Autre"
};

export default function RoadTypeChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch(`${API_BASE}/api/stats/road-types/`)
            .then(res => res.json())
            .then(rawData => {
                const formattedData = rawData.map(item => ({
                    ...item,
                    name: ROAD_LABELS[item.catr] || `Code ${item.catr}`
                }));
                setData(formattedData);
            });
    }, []);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                    dataKey="name" 
                    angle={-45} 
                    textAnchor="end" 
                    interval={0}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="total" fill="#3182CE" radius={[4, 4, 0, 0]} />
            </BarChart>
        </ResponsiveContainer>
    );
}