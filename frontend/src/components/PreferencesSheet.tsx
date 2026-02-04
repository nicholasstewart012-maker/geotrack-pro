import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Moon, Bell, ChevronLeft, Volume2, Globe } from 'lucide-react';

interface PreferencesSheetProps {
    isOpen: boolean;
    onClose: () => void;
}

export const PreferencesSheet: React.FC<PreferencesSheetProps> = ({ isOpen, onClose }) => {
    const [darkMode, setDarkMode] = useState(true);
    const [notifications, setNotifications] = useState(true);
    const [sound, setSound] = useState(true);

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
                        <div className="absolute top-0 left-0 w-full h-32 bg-orange-500/10 -z-10 blur-3xl" />

                        <div className="flex justify-between items-center mb-6">
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white active:bg-white/10 transition-colors"
                            >
                                <ChevronLeft size={20} />
                            </button>
                            <h2 className="text-xl font-black text-white">Preferences</h2>
                            <div className="w-10" />
                        </div>

                        <div className="space-y-4">
                            {/* Dark Mode Toggle */}
                            <div className="ios-card p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400">
                                        <Moon size={20} />
                                    </div>
                                    <div className="text-left">
                                        <p className="text-xs font-black text-white uppercase tracking-wider">Dark Theme</p>
                                        <p className="text-[10px] text-ios-secondary font-bold">Always On</p>
                                    </div>
                                </div>
                                <div
                                    onClick={() => setDarkMode(!darkMode)}
                                    className={`w-12 h-7 rounded-full p-1 transition-colors cursor-pointer ${darkMode ? 'bg-ios-green' : 'bg-white/20'}`}
                                >
                                    <motion.div
                                        layout
                                        className="w-5 h-5 bg-white rounded-full shadow-sm"
                                        animate={{ x: darkMode ? 20 : 0 }}
                                    />
                                </div>
                            </div>

                            {/* Notifications Toggle */}
                            <div className="ios-card p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center text-red-400">
                                        <Bell size={20} />
                                    </div>
                                    <div className="text-left">
                                        <p className="text-xs font-black text-white uppercase tracking-wider">Notifications</p>
                                        <p className="text-[10px] text-ios-secondary font-bold">Push Alerts</p>
                                    </div>
                                </div>
                                <div
                                    onClick={() => setNotifications(!notifications)}
                                    className={`w-12 h-7 rounded-full p-1 transition-colors cursor-pointer ${notifications ? 'bg-ios-green' : 'bg-white/20'}`}
                                >
                                    <motion.div
                                        layout
                                        className="w-5 h-5 bg-white rounded-full shadow-sm"
                                        animate={{ x: notifications ? 20 : 0 }}
                                    />
                                </div>
                            </div>

                            {/* Sound Toggle */}
                            <div className="ios-card p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
                                        <Volume2 size={20} />
                                    </div>
                                    <div className="text-left">
                                        <p className="text-xs font-black text-white uppercase tracking-wider">Sound Effects</p>
                                        <p className="text-[10px] text-ios-secondary font-bold">In-App Audio</p>
                                    </div>
                                </div>
                                <div
                                    onClick={() => setSound(!sound)}
                                    className={`w-12 h-7 rounded-full p-1 transition-colors cursor-pointer ${sound ? 'bg-ios-green' : 'bg-white/20'}`}
                                >
                                    <motion.div
                                        layout
                                        className="w-5 h-5 bg-white rounded-full shadow-sm"
                                        animate={{ x: sound ? 20 : 0 }}
                                    />
                                </div>
                            </div>

                            <div className="mt-8 text-center px-8">
                                <p className="text-[9px] text-white/30 leading-relaxed font-medium">
                                    Changing these settings will effectively do nothing right now because this is a demo, but they look nice don't they?
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
