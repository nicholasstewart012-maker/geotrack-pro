import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, AlertCircle } from 'lucide-react';
import { cn } from '../lib/utils';

interface EditScheduleModalProps {
    isOpen: boolean;
    onClose: () => void;
    schedule: any;
    onSave: (scheduleId: number, updates: any) => void;
    isSubmitting: boolean;
}

export const EditScheduleModal: React.FC<EditScheduleModalProps> = ({ isOpen, onClose, schedule, onSave, isSubmitting }) => {
    const [interval, setInterval] = useState('');
    const [lastPerformed, setLastPerformed] = useState('');

    useEffect(() => {
        if (schedule) {
            setInterval(schedule.interval_value.toString());
            setLastPerformed(schedule.last_performed_value.toString());
        }
    }, [schedule]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(schedule.id, {
            interval_value: parseFloat(interval),
            last_performed_value: parseFloat(lastPerformed)
        });
    };

    if (!isOpen || !schedule) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 20 }}
                    className="relative w-full max-w-sm bg-ios-bg rounded-[2rem] border border-white/10 shadow-2xl overflow-hidden"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

                    <div className="relative p-6 space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-xl font-black text-white">Edit Cycle</h3>
                                <p className="text-xs text-ios-secondary font-medium uppercase tracking-wider">{schedule.task_name}</p>
                            </div>
                            <button
                                onClick={onClose}
                                className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90 transition-all"
                            >
                                <X size={16} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-widest pl-1">
                                    Service Interval ({schedule.tracking_type})
                                </label>
                                <div className="space-y-1">
                                    <input
                                        type="number"
                                        value={interval}
                                        onChange={(e) => setInterval(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white font-bold placeholder:text-white/20 focus:outline-none focus:border-ios-blue transition-colors"
                                        placeholder="e.g. 5000"
                                    />
                                    <p className="text-[10px] text-ios-secondary px-1">
                                        How often this service should be performed.
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-widest pl-1">
                                    Last Performed At
                                </label>
                                <input
                                    type="number"
                                    value={lastPerformed}
                                    onChange={(e) => setLastPerformed(e.target.value)}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white font-bold placeholder:text-white/20 focus:outline-none focus:border-ios-blue transition-colors"
                                    placeholder="e.g. 105000"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className={cn(
                                    "w-full py-4 rounded-xl font-black uppercase tracking-wider text-sm shadow-lg active:scale-[0.98] transition-all flex items-center justify-center gap-2",
                                    isSubmitting ? "bg-white/10 text-white/50" : "bg-ios-blue text-white shadow-ios-blue/25"
                                )}
                            >
                                {isSubmitting ? <span className="animate-pulse">Saving...</span> : (
                                    <>
                                        <Save size={16} />
                                        Save Changes
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};
