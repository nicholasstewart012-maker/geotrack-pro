import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Truck, Trash2 } from 'lucide-react';
import { cn, formatMileage } from '../lib/utils';

interface VehicleCardProps {
    vehicle: any;
    index: number;
    onLogClick: () => void;
    onHistoryClick: () => void;
    onDelete: () => void;
}

export const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, index, onLogClick, onHistoryClick, onDelete }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="ios-card overflow-hidden relative group"
        >
            <div className="p-5 space-y-4">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <h3 className="font-black text-xl text-white tracking-tight">{vehicle.name}</h3>
                        <span className="inline-block text-[10px] text-ios-secondary font-black uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded">
                            {vehicle.vin || 'VIN NOT SET'}
                        </span>
                    </div>

                    <div className="flex gap-2">
                        <div className={cn(
                            "flex items-center gap-1.5 px-3 py-1.5 rounded-xl border font-black text-[10px] uppercase shadow-inner",
                            vehicle.current_mileage % 5000 < 500
                                ? 'bg-ios-red/10 border-ios-red/20 text-ios-red animate-pulse'
                                : 'bg-ios-green/10 border-ios-green/20 text-ios-green'
                        )}>
                            <Activity size={12} />
                            {vehicle.current_mileage % 5000 < 500 ? 'Critical' : 'Healthy'}
                        </div>

                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete();
                            }}
                            className="w-8 h-8 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center active:scale-90 transition-all hover:bg-red-500/20"
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>

                </div>

                <div className="flex gap-3">
                    <div className="flex-1 bg-white/5 p-4 rounded-3xl border border-white/5">
                        <p className="text-[10px] font-black text-ios-secondary uppercase mb-1">Mileage</p>
                        <h4 className="text-xl font-black text-white">{formatMileage(vehicle.current_mileage)} <span className="text-xs font-bold text-ios-secondary">MI</span></h4>
                    </div>
                    <div className="flex-1 bg-white/5 p-4 rounded-3xl border border-white/5">
                        <p className="text-[10px] font-black text-ios-secondary uppercase mb-1">Runtime</p>
                        <h4 className="text-xl font-black text-white">{vehicle.current_hours.toFixed(1)} <span className="text-xs font-bold text-ios-secondary">HR</span></h4>
                    </div>
                </div>

                <div className="space-y-3 pt-2">
                    <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-wider text-ios-secondary">
                        <span>Next Service Cycle</span>
                        <span className="text-white">{(vehicle.current_mileage % 5000).toFixed(0)} / 5,000 MI</span>
                    </div>
                    <div className="h-2.5 w-full bg-white/10 rounded-full overflow-hidden border border-white/5 p-[1px]">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(vehicle.current_mileage % 5000) / 50}%` }}
                            className={cn(
                                "h-full rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)]",
                                vehicle.current_mileage % 5000 < 500 ? 'bg-ios-red' : 'bg-ios-blue'
                            )}
                        />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 border-t border-white/5">
                <button
                    onClick={onLogClick}
                    className="py-4 text-xs font-black uppercase text-ios-blue tap-highlight-none active:bg-white/5 transition-colors"
                >
                    Log Entry
                </button>
                <button
                    onClick={onHistoryClick}
                    className="py-4 text-xs font-black uppercase text-ios-secondary border-l border-white/5 tap-highlight-none active:bg-white/5 transition-colors"
                >
                    History
                </button>
            </div>
        </motion.div>
    );
};
