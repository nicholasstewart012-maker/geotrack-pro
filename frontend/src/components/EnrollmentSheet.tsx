import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../lib/utils';

interface EnrollmentSheetProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    newVehicle: any;
    setNewVehicle: any;
    isSubmitting: boolean;
}

export const EnrollmentSheet: React.FC<EnrollmentSheetProps> = ({
    isOpen, onClose, onSubmit, newVehicle, setNewVehicle, isSubmitting
}) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center px-4 pb-10">
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
                        className="w-full max-w-md bg-[#1C1C1E] rounded-t-[40px] sm:rounded-[40px] shadow-2xl relative z-10 border-t border-white/10 p-8 pb-12"
                    >
                        <div className="w-12 h-1.5 bg-white/10 rounded-full mx-auto mb-8"></div>

                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-3xl font-black text-white">Enrollment</h2>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={onSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Asset Name</label>
                                <input
                                    required
                                    value={newVehicle.name}
                                    onChange={(e) => setNewVehicle({ ...newVehicle, name: e.target.value })}
                                    placeholder="e.g. Logistic Unit 10"
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/20 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">Geotab Serial</label>
                                <input
                                    required
                                    value={newVehicle.geotab_id}
                                    onChange={(e) => setNewVehicle({ ...newVehicle, geotab_id: e.target.value })}
                                    placeholder="G9-XXXX-XXXX"
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/20 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-ios-secondary uppercase tracking-[0.2em] ml-1">VIN (Optional)</label>
                                <input
                                    value={newVehicle.vin}
                                    onChange={(e) => setNewVehicle({ ...newVehicle, vin: e.target.value })}
                                    placeholder="17-Digit Vehicle ID"
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/20 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                />
                            </div>

                            <button
                                disabled={isSubmitting}
                                className={cn(
                                    "w-full bg-ios-blue text-white font-black py-5 rounded-3xl shadow-xl shadow-ios-blue/30 active:scale-[0.98] transition-all mt-4",
                                    isSubmitting && "opacity-50 grayscale"
                                )}
                            >
                                {isSubmitting ? 'Validating Link...' : 'Finish Enrollment'}
                            </button>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
