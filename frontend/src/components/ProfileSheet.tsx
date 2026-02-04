import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, LogOut, User as UserIcon, Shield, Settings, ChevronRight } from 'lucide-react';

interface ProfileSheetProps {
    isOpen: boolean;
    onClose: () => void;
    onLogout: () => void;
    onSecurityClick: () => void;
    onPreferencesClick: () => void;
    user: { email: string; full_name?: string };
}

export const ProfileSheet: React.FC<ProfileSheetProps> = ({
    isOpen, onClose, onLogout, onSecurityClick, onPreferencesClick, user
}) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[150] flex items-center justify-center p-6">
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

                        <div className="flex justify-between items-start mb-8">
                            <div className="w-16 h-16 bg-ios-blue rounded-3xl flex items-center justify-center shadow-lg shadow-ios-blue/20">
                                <UserIcon className="text-white" size={32} />
                            </div>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white active:bg-white/10 transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="space-y-1 mb-8">
                            <h2 className="text-2xl font-black text-white">{user.full_name || 'Fleet Admin'}</h2>
                            <p className="text-ios-blue text-[10px] font-bold uppercase tracking-widest">{user.email}</p>
                        </div>

                        <div className="space-y-3">
                            <button
                                onClick={onSecurityClick}
                                className="w-full ios-card p-4 flex items-center justify-between group active:bg-white/5 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-xl bg-ios-blue/10 flex items-center justify-center text-ios-blue">
                                        <Shield size={16} />
                                    </div>
                                    <span className="text-xs font-black text-white uppercase tracking-wider">Security Access</span>
                                </div>
                                <ChevronRight size={14} className="text-white/20 group-hover:text-white/40 transition-colors" />
                            </button>

                            <button
                                onClick={onPreferencesClick}
                                className="w-full ios-card p-4 flex items-center justify-between group active:bg-white/5 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-500">
                                        <Settings size={16} />
                                    </div>
                                    <span className="text-xs font-black text-white uppercase tracking-wider">Account Preferences</span>
                                </div>
                                <ChevronRight size={14} className="text-white/20 group-hover:text-white/40 transition-colors" />
                            </button>

                            <div className="pt-4 mt-4 border-t border-white/5">
                                <button
                                    onClick={onLogout}
                                    className="w-full bg-red-500/10 text-red-500 font-black py-4 rounded-2xl flex items-center justify-center gap-2 active:bg-red-500/20 transition-colors uppercase text-[10px] tracking-widest"
                                >
                                    <LogOut size={16} />
                                    Terminate Session
                                </button>
                            </div>
                        </div>

                        <div className="mt-8 text-center">
                            <p className="text-[8px] text-white/20 font-black uppercase tracking-[0.3em]">GeoTrack Pro Enterprise v1.2</p>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
