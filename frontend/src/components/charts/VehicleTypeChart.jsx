import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    CartesianGrid, Cell
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const { group, total, members, color } = payload[0].payload;
        return (
            <div style={{
                background: 'white',
                border: '1px solid #E2E8F0',
                borderRadius: 8,
                padding: '10px 14px',
                fontSize: 13,
                minWidth: 220,
                maxWidth: 300,
            }}>
                <p style={{ fontWeight: 600, color, marginBottom: 6 }}>{group}</p>
                <p style={{ color: '#2D3748', marginBottom: 8 }}>
                    {total.toLocaleString('fr-FR')} véhicules impliqués
                </p>
                <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: 8 }}>
                    <p style={{ color: '#A0AEC0', fontSize: 11, marginBottom: 4 }}>
                        Inclus dans ce groupe :
                    </p>
                    {members.map(m => (
                        <div key={m} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            margin: '2px 0',
                            color: '#4A5568',
                        }}>
                            <span style={{
                                width: 5,
                                height: 5,
                                borderRadius: '50%',
                                background: color,
                                flexShrink: 0,
                            }} />
                            {m}
                        </div>
                    ))}
                </div>
            </div>
        );
    }
    return null;
};

export default function VehicleTypeChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/stats/vehicle-types/')
            .then(res => {
                if (!res.ok) throw new Error("Erreur réseau");
                return res.json();
            })
            .then(raw => {
                if (Array.isArray(raw)) setData(raw);
            })
            .catch(err => console.error("Erreur chargement véhicules:", err));
    }, []);

    return (
        <div style={{ width: '100%', height: '420px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                        dataKey="group"
                        angle={-25}
                        textAnchor="end"
                        interval={0}
                        tick={{ fontSize: 12 }}
                        height={80}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                    <Bar dataKey="total" radius={[4, 4, 0, 0]}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
