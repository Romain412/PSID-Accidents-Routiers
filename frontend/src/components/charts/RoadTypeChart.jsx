import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

// Libellés officiels selon la documentation du fichier LIEUX
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
        fetch('https://psid-accidents-routiers.onrender.com/api/stats/road-types/')
            .then(res => res.json())
            .then(rawData => {
                // Conversion des codes catr en noms lisibles
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