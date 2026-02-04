import React from 'react';
import { motion } from 'framer-motion';

interface LineChartProps {
    data: number[];
    labels: string[];
    color?: string;
}

export const LineChart: React.FC<LineChartProps> = ({ data, labels, color = '#0A84FF' }) => {
    const width = 400;
    const height = 150;
    const padding = 20;

    const max = Math.max(...data) || 100;
    const min = 0;

    const points = data.map((d, i) => {
        const x = (i / (data.length - 1)) * (width - padding * 2) + padding;
        const y = height - ((d - min) / (max - min)) * (height - padding * 2) - padding;
        return `${x},${y}`;
    }).join(' ');

    const areaPoints = `
    ${padding},${height - padding} 
    ${points} 
    ${width - padding},${height - padding}
  `;

    return (
        <div className="w-full h-full">
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
                <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                        <stop offset="100%" stopColor={color} stopOpacity="0" />
                    </linearGradient>
                </defs>

                {/* Grid Lines */}
                {[0, 0.5, 1].map((p) => {
                    const y = height - (p * (height - padding * 2)) - padding;
                    return (
                        <line
                            key={p}
                            x1={padding}
                            y1={y}
                            x2={width - padding}
                            y2={y}
                            stroke="rgba(255,255,255,0.05)"
                            strokeWidth="1"
                        />
                    );
                })}

                {/* Area */}
                <motion.path
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    d={`M ${areaPoints}`}
                    fill="url(#chartGradient)"
                />

                {/* Line */}
                <motion.polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    points={points}
                />

                {/* Data Points */}
                {data.map((d, i) => {
                    const x = (i / (data.length - 1)) * (width - padding * 2) + padding;
                    const y = height - ((d - min) / (max - min)) * (height - padding * 2) - padding;
                    return (
                        <motion.circle
                            key={i}
                            cx={x}
                            cy={y}
                            r="4"
                            fill="#1C1C1E"
                            stroke={color}
                            strokeWidth="2"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.5 + i * 0.1 }}
                        />
                    );
                })}
            </svg>
        </div>
    );
};
