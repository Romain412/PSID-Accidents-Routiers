import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

export default function RainCorrelationChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/stats/rain-correlation/')
            .then(res => res.json())
            .then(rawData => {
                // On s'assure que les données sont triées par volume pour un meilleur visuel
                const sortedData = [...rawData].sort((a, b) => b.total - a.total);
                setData(sortedData);
            })
            .catch(err => console.error("Erreur de chargement météo:", err));
    }, []);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart 
                data={data} 
                margin={{ top: 10, right: 30, left: 20, bottom: 70 }}
            >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                    dataKey="atm"  // Doit correspondre exactement à la clé du backend
                    angle={-45} 
                    textAnchor="end" 
                    interval={0} 
                    height={60}
                />
                <YAxis />
                <Tooltip cursor={{ fill: 'rgba(0, 0, 0, 0.1)' }} />
                <Bar 
                    dataKey="total" 
                    fill="#3182CE" 
                    radius={[4, 4, 0, 0]} 
                />
            </BarChart>
        </ResponsiveContainer>
    );
}