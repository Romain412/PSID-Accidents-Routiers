import React, { useEffect, useState } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Cell
} from 'recharts';

// Couleurs saisonnières pour différencier les 4 barres
const COLORS = ['#3182CE', '#38A169', '#E53E3E', '#DD6B20']; 

export default function HolidayChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        // Appel à l'endpoint qui renvoie les 4 périodes (Hiver, Printemps, Été, Automne)
        fetch('https://psid-accidents-routiers.onrender.com/api/stats/holiday-periods/')
            .then(res => res.json())
            .then(setData)
            .catch(err => console.error("Erreur chargement périodes:", err));
    }, []);

    return (
        <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                    data={data} 
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="periode"/>
                    <YAxis />
                    <Tooltip cursor={{ fill: 'rgba(0, 0, 0, 0.1)' }} />
                    <Bar 
                        dataKey="total" 
                        radius={[4, 4, 0, 0]}
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}