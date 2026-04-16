import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

export default function AgeAccidentChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        // Vérifie bien que l'URL correspond à ton urls.py (stats/age-distribution/)
        fetch('http://localhost:8000/api/stats/age-distribution/')
            .then(res => {
                if (!res.ok) throw new Error("Erreur réseau");
                return res.json();
            })
            .then(data => {
                // On s'assure que c'est bien un tableau avant de mettre à jour le state
                if (Array.isArray(data)) {
                    setData(data);
                }
            })
            .catch(err => console.error("Erreur chargement âge:", err));
    }, []);

    return (
        /* Important : Le parent de ResponsiveContainer doit avoir une hauteur fixe (ex: 400px) */
        <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                    data={data} 
                    margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis 
                        dataKey="age_range" // Doit correspondre à la clé du dictionnaire buckets dans views.py
                    />
                    <YAxis />
                    <Tooltip cursor={{ fill: 'rgba(0, 0, 0, 0.1)' }} />
                    <Bar 
                        dataKey="total" // Doit correspondre à la clé générée dans ton dictionnaire final
                        fill="#38A169" 
                        radius={[4, 4, 0, 0]} 
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}