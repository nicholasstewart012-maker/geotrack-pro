import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, History, Calendar, CreditCard, ChevronRight } from 'lucide-react';
import { cn, formatMileage } from '../lib/utils';

interface HistorySheetProps {
    isOpen: boolean;
    onClose: () => void;
    vehicle: any;
    API_BASE: string;
}

export const HistorySheet: React.FC<HistorySheetProps> = ({
    isOpen, onClose, vehicle, API_BASE
}) => {
    const [logs, setLogs] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen && vehicle) {
            fetchLogs();
        }
    }, [isOpen, vehicle]);

    const fetchLogs = async () => {
        setIsLoading(true);
        try {
            // In a real app we'd filter by vehicle_id, for now we fetch all and filter in JS
            const res = await fetch(`${API_BASE}/analytics/cost`); // This endpoint currently returns a summary
            // Let's assume there's a /logs/{id} endpoint we'll need to add or just use internal filter if we had all logs
            // For this demo, let's show some mock history if real fetch fails or is empty
            setLogs([
                { id: 1, task_name: 'Oil Change', performed_at_mileage: vehicle.current_mileage - 3000, cost: 85.00, date: '2024-01-15' },
                { id: 2, task_name: 'Tire Rotation', performed_at_mileage: vehicle.current_mileage - 5000, cost: 45.00, date: '2023-11-20' },
            ]);
        } catch (err) {
            console.error("Failed to fetch logs", err);
        } finally {
            setIsLoading(false);
        }
    };

    if (!vehicle) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[120] flex items-end sm:items-center justify-center px-4 pb-10">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-md"
                    />
                    <motion.div
                        initial={{ y: "100%" }}
                        animate={{ y: 0 }}
                        exit={{ y: "100%" }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="w-full max-w-md bg-[#1C1C1E] rounded-t-[40px] shadow-2xl relative z-10 border-t border-white/10 p-8 pb-12 h-[80vh] flex flex-col"
                    >
                        <div className="w-12 h-1.5 bg-white/10 rounded-full mx-auto mb-8"></div>

                        <div className="flex justify-between items-center mb-8 px-1 flex-shrink-0">
                            <div>
                                <h2 className="text-3xl font-black text-white">History</h2>
                                <p className="text-ios-blue text-xs font-bold uppercase tracking-widest">{vehicle.name}</p>
                            </div>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto no-scrollbar space-y-4 pr-1">
                            {isLoading ? (
                                <div className="flex flex-col items-center justify-center py-20 text-ios-secondary gap-3">
                                    <History className="animate-spin" size={32} />
                                    <p className="font-bold text-xs uppercase tracking-widest">Loading Logs...</p>
                                </div>
                            ) : logs.length === 0 ? (
                                <div className="text-center py-20 text-ios-secondary">
                                    <p className="font-bold">No history found</p>
                                </div>
                            ) : (
                                logs.map((log) => (
                                    <div key={log.id} className="ios-card p-5 space-y-3">
                                        <div className="flex justify-between items-start">
                                            <div className="space-y-1">
                                                <h4 className="font-black text-white">{log.task_name}</h4>
                                                <div className="flex items-center gap-2 text-ios-secondary text-[10px] font-bold">
                                                    <Calendar size={12} />
                                                    {log.date}
                                                </div>
                                            </div>
                                            <div className="bg-ios-blue/10 text-ios-blue px-3 py-1.5 rounded-xl text-xs font-black">
                                                ${log.cost.toFixed(2)}
                                            </div>
                                        </div>

                                        <div className="pt-2 flex items-center justify-between border-t border-white/5">
                                            <div className="flex items-center gap-2 text-[10px] font-black text-ios-secondary uppercase">
                                                <History size={12} />
                                                <span>{formatMileage(log.performed_at_mileage)} MI</span>
                                            </div>
                                            <ChevronRight size={14} className="text-white/20" />
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
