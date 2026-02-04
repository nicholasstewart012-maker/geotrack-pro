import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, Gauge, Clock, CreditCard } from 'lucide-react';
import { cn, formatMileage } from '../lib/utils';

interface LogSheetProps {
    isOpen: boolean;
    onClose: () => void;
    vehicle: any;
    onSubmit: (log: any) => void;
    isSubmitting: boolean;
}

export const LogSheet: React.FC<LogSheetProps> = ({
    isOpen, onClose, vehicle, onSubmit, isSubmitting
}) => {
    const [log, setLog] = useState({
        vehicle_id: vehicle?.id,
        task_name: 'Regular Maintenance',
        performed_at_mileage: vehicle?.current_mileage || 0,
        performed_at_hours: vehicle?.current_hours || 0,
        cost: 0,
        notes: ''
    });

    if (!vehicle) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[110] flex items-end sm:items-center justify-center px-4 pb-10">
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
                        className="w-full max-w-md bg-[#1C1C1E] rounded-t-[40px] shadow-2xl relative z-10 border-t border-white/10 p-8 pb-12"
                    >
                        <div className="w-12 h-1.5 bg-white/10 rounded-full mx-auto mb-8"></div>

                        <div className="flex justify-between items-center mb-8 px-1">
                            <div>
                                <h2 className="text-3xl font-black text-white">Log Entry</h2>
                                <p className="text-ios-blue text-xs font-bold uppercase tracking-widest">{vehicle.name}</p>
                            </div>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="space-y-6 max-h-[60vh] overflow-y-auto no-scrollbar pr-1">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Service Task</label>
                                <input
                                    required
                                    value={log.task_name}
                                    onChange={(e) => setLog({ ...log, task_name: e.target.value })}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Mileage</label>
                                    <div className="relative">
                                        <Gauge className="absolute left-4 top-1/2 -translate-y-1/2 text-ios-secondary" size={16} />
                                        <input
                                            type="number"
                                            value={log.performed_at_mileage}
                                            onChange={(e) => setLog({ ...log, performed_at_mileage: parseFloat(e.target.value) })}
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 pl-12 text-white outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Runtime (HR)</label>
                                    <div className="relative">
                                        <Clock className="absolute left-4 top-1/2 -translate-y-1/2 text-ios-secondary" size={16} />
                                        <input
                                            type="number"
                                            value={log.performed_at_hours}
                                            onChange={(e) => setLog({ ...log, performed_at_hours: parseFloat(e.target.value) })}
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 pl-12 text-white outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Estimated Cost ($)</label>
                                <div className="relative">
                                    <CreditCard className="absolute left-4 top-1/2 -translate-y-1/2 text-ios-secondary" size={16} />
                                    <input
                                        type="number"
                                        value={log.cost}
                                        onChange={(e) => setLog({ ...log, cost: parseFloat(e.target.value) })}
                                        className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 pl-12 text-white outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                    />
                                </div>
                            </div>

                            <button
                                onClick={() => onSubmit(log)}
                                disabled={isSubmitting}
                                className={cn(
                                    "w-full bg-ios-blue text-white font-black py-5 rounded-3xl shadow-xl shadow-ios-blue/30 active:scale-[0.98] transition-all mt-6 flex items-center justify-center gap-2",
                                    isSubmitting && "opacity-50 grayscale"
                                )}
                            >
                                <CheckCircle2 size={20} />
                                {isSubmitting ? 'Logging...' : 'Confirm Service'}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
