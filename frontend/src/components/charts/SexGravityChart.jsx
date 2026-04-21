import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    CartesianGrid, Legend
} from 'recharts';

// Couleurs par libellé exact stocké en base (MAP_GRAV dans import_csv.py)
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
                <p style={{ fontWeight: 600, marginBottom: 6 }}>{label}</p>
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

export default function SexGravityChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/stats/sex-gravity/')
            .then(res => {
                if (!res.ok) throw new Error("Erreur réseau");
                return res.json();
            })
            .then(raw => {
                if (Array.isArray(raw)) setData(raw);
            })
            .catch(err => console.error("Erreur chargement sexe/gravité:", err));
    }, []);

    return (
        <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                    barCategoryGap="30%"
                    barGap={2}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    {/*
                      * dataKey="sexe" correspond à la clé retournée par stats_sex_gravity(),
                      * dont les valeurs sont 'Masculin' / 'Féminin' (MAP_SEXE dans import_csv.py)
                    */}
                    <XAxis dataKey="sexe" tick={{ fontSize: 13 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 13 }} />

                    <Bar dataKey="Tué"                fill={GRAVITY_COLORS['Tué']}                stackId="a" />
                    <Bar dataKey="Blessé hospitalisé" fill={GRAVITY_COLORS['Blessé hospitalisé']} stackId="a" />
                    <Bar dataKey="Blessé léger"       fill={GRAVITY_COLORS['Blessé léger']}       stackId="a" />
                    <Bar dataKey="Indemne"            fill={GRAVITY_COLORS['Indemne']}            stackId="a" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
