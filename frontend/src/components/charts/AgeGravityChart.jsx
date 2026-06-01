import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    CartesianGrid, Legend
} from 'recharts';
import { API_BASE } from '../../config';

const GRAVITY_COLORS = {
    'Tué':                '#C53030',
    'Blessé hospitalisé': '#DD6B20',
    'Blessé léger':       '#D69E2E',
    'Indemne':            '#38A169',
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        const total = payload.reduce((sum, p) => sum + p.value, 0);
        return (
            <div style={{
                background: 'white',
                border: '1px solid #E2E8F0',
                borderRadius: 8,
                padding: '10px 14px',
                fontSize: 13,
                minWidth: 220,
            }}>
                <p style={{ fontWeight: 600, marginBottom: 6 }}>Tranche {label} ans</p>
                {payload.map(p => {
                    const pct = total > 0 ? ((p.value / total) * 100).toFixed(1) : '0.0';
                    return (
                        <div key={p.name} style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            gap: 12,
                            margin: '3px 0',
                        }}>
                            <span style={{ color: p.fill }}>{p.name}</span>
                            <span style={{ color: '#2D3748', fontVariantNumeric: 'tabular-nums' }}>
                                {p.value.toLocaleString('fr-FR')}
                                <span style={{ color: '#A0AEC0', marginLeft: 6 }}>({pct}%)</span>
                            </span>
                        </div>
                    );
                })}
                <div style={{ borderTop: '1px solid #E2E8F0', marginTop: 6, paddingTop: 6, display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#718096' }}>Total</span>
                    <span style={{ color: '#2D3748', fontWeight: 600 }}>{total.toLocaleString('fr-FR')}</span>
                </div>
            </div>
        );
    }
    return null;
};

export default function AgeGravityChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch(`${API_BASE}/api/stats/age-gravity/`)
            .then(res => {
                if (!res.ok) throw new Error("Erreur réseau");
                return res.json();
            })
            .then(raw => {
                if (Array.isArray(raw)) setData(raw);
            })
            .catch(err => console.error("Erreur chargement âge/gravité:", err));
    }, []);

    return (
        <div style={{ width: '100%', height: '420px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ top: 10, right: 30, left: 70, bottom: 10 }}
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 12 }} />
                    <YAxis
                        type="category"
                        dataKey="age_range"
                        tick={{ fontSize: 13 }}
                        width={65}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 13 }} />

                    <Bar dataKey="Tué"                fill={GRAVITY_COLORS['Tué']}                stackId="a" />
                    <Bar dataKey="Blessé hospitalisé" fill={GRAVITY_COLORS['Blessé hospitalisé']} stackId="a" />
                    <Bar dataKey="Blessé léger"       fill={GRAVITY_COLORS['Blessé léger']}       stackId="a" />
                    <Bar dataKey="Indemne"            fill={GRAVITY_COLORS['Indemne']}            stackId="a" radius={[0, 4, 4, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
