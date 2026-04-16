import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

export default function VehicleTypeChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/stats/vehicle-types/')
            .then(res => res.json())
            .then(rawData => {
                if (!Array.isArray(rawData)) return;
                
                // On trie simplement par nombre d'accidents décroissant pour la lisibilité
                const sortedData = [...rawData].sort((a, b) => b.total - a.total);
                setData(sortedData);
            })
            .catch(err => console.error("Erreur API:", err));
    }, []);

    return (
        <ResponsiveContainer width="100%" height={500}>
            <BarChart 
                data={data} 
                margin={{ top: 20, right: 30, left: 20, bottom: 150 }} // Marge basse augmentée pour les longs labels
            >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                    dataKey="catv" 
                    angle={-45} 
                    textAnchor="end" 
                    interval={0} 
                    height={120} 
                    style={{ fontSize: '12px' }}
                />
                <YAxis />
                <Tooltip cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} />
                <Bar dataKey="total" radius={[4, 4, 0, 0]}>
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}