import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Lock, Save, ChevronLeft } from 'lucide-react';

interface SecuritySheetProps {
    isOpen: boolean;
    onClose: () => void;
    API_BASE?: string;
}

export const SecuritySheet: React.FC<SecuritySheetProps> = ({ isOpen, onClose, API_BASE }) => {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            alert("New passwords do not match");
            return;
        }

        setIsSubmitting(true);
        // Simulate API call for now, since we haven't built the password change endpoint yet
        await new Promise(resolve => setTimeout(resolve, 1500));
        alert("Password updated successfully (This logic is simulated until backend endpoint is live).");
        setIsSubmitting(false);
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[160] flex items-center justify-center p-6">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-xl"
                    />
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className="w-full max-w-sm bg-[#1C1C1E] rounded-[40px] shadow-2xl relative z-10 border border-white/10 p-8 overflow-hidden"
                    >
                        <div className="absolute top-0 left-0 w-full h-32 bg-ios-blue/10 -z-10 blur-3xl" />

                        <div className="flex justify-between items-center mb-6">
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white active:bg-white/10 transition-colors"
                            >
                                <ChevronLeft size={20} />
                            </button>
                            <h2 className="text-xl font-black text-white">Security</h2>
                            <div className="w-10" />
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-ios-secondary tracking-widest pl-3">Current Password</label>
                                <div className="ios-input-group flex items-center px-4 py-3 bg-white/5 rounded-2xl border border-white/5 focus-within:border-ios-blue/50 transition-colors">
                                    <Lock size={16} className="text-ios-secondary mr-3" />
                                    <input
                                        type="password"
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        className="bg-transparent border-none outline-none text-white text-sm w-full font-medium placeholder:text-white/20"
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-ios-secondary tracking-widest pl-3">New Password</label>
                                <div className="ios-input-group flex items-center px-4 py-3 bg-white/5 rounded-2xl border border-white/5 focus-within:border-ios-blue/50 transition-colors">
                                    <Lock size={16} className="text-ios-secondary mr-3" />
                                    <input
                                        type="password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        className="bg-transparent border-none outline-none text-white text-sm w-full font-medium placeholder:text-white/20"
                                        placeholder="New Password"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-1">
                                <label className="text-[10px] uppercase font-bold text-ios-secondary tracking-widest pl-3">Confirm New Password</label>
                                <div className="ios-input-group flex items-center px-4 py-3 bg-white/5 rounded-2xl border border-white/5 focus-within:border-ios-blue/50 transition-colors">
                                    <Lock size={16} className="text-ios-secondary mr-3" />
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className="bg-transparent border-none outline-none text-white text-sm w-full font-medium placeholder:text-white/20"
                                        placeholder="Confirm Password"
                                        required
                                    />
                                </div>
                            </div>

                            <button
                                disabled={isSubmitting}
                                type="submit"
                                className="w-full bg-ios-blue text-white font-black py-4 rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-ios-blue/20 active:scale-95 transition-all mt-6 disabled:opacity-50"
                            >
                                {isSubmitting ? <span className="animate-spin">⏳</span> : <Save size={18} />}
                                <span className="uppercase text-[10px] tracking-widest">Update Security</span>
                            </button>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
