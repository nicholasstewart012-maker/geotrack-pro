import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Server, Database, Mail } from 'lucide-react';
import { cn } from '../lib/utils';

interface ConfigSheetProps {
    isOpen: boolean;
    onClose: () => void;
    settings: any;
    onSave: (settings: any) => void;
    isSubmitting: boolean;
}

export const ConfigSheet: React.FC<ConfigSheetProps> = ({
    isOpen, onClose, settings, onSave, isSubmitting
}) => {
    const [localSettings, setLocalSettings] = useState(settings);

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
                            <h2 className="text-3xl font-black text-white px-1">Settings</h2>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="space-y-6 max-h-[60vh] overflow-y-auto no-scrollbar pr-1">
                            {/* Geotab Section */}
                            <div className="space-y-4">
                                <div className="flex items-center gap-2 px-1 text-ios-blue">
                                    <Server size={14} />
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em]">Geotab Integration</p>
                                </div>
                                <div className="space-y-3">
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-ios-secondary ml-1">Server URL</label>
                                        <input
                                            value={localSettings.geotab_server}
                                            onChange={(e) => setLocalSettings({ ...localSettings, geotab_server: e.target.value })}
                                            placeholder="my3.geotab.com"
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-ios-secondary ml-1">Database Name</label>
                                        <input
                                            value={localSettings.geotab_db}
                                            onChange={(e) => setLocalSettings({ ...localSettings, geotab_db: e.target.value })}
                                            placeholder="corp_fleet_db"
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-ios-secondary ml-1">Username</label>
                                        <input
                                            value={localSettings.geotab_user}
                                            onChange={(e) => setLocalSettings({ ...localSettings, geotab_user: e.target.value })}
                                            placeholder="admin@company.com"
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-ios-secondary ml-1">Password</label>
                                        <input
                                            type="password"
                                            value={localSettings.geotab_pass}
                                            onChange={(e) => setLocalSettings({ ...localSettings, geotab_pass: e.target.value })}
                                            placeholder="••••••••"
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Alert Section */}
                            <div className="space-y-4 pt-4 border-t border-white/5">
                                <div className="flex items-center gap-2 px-1 text-ios-amber">
                                    <Mail size={14} />
                                    <p className="text-[10px] font-black uppercase tracking-[0.2em]">Maintenance Alerts</p>
                                </div>
                                <div className="space-y-1">
                                    <label className="text-[10px] font-bold text-ios-secondary ml-1">Admin Email Address</label>
                                    <input
                                        value={localSettings.admin_email}
                                        onChange={(e) => setLocalSettings({ ...localSettings, admin_email: e.target.value })}
                                        placeholder="fleet-admin@company.com"
                                        className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                    />
                                </div>
                            </div>

                            <button
                                onClick={() => onSave(localSettings)}
                                disabled={isSubmitting}
                                className={cn(
                                    "w-full bg-white text-black font-black py-5 rounded-3xl shadow-xl active:scale-[0.98] transition-all mt-6 flex items-center justify-center gap-2",
                                    isSubmitting && "opacity-50"
                                )}
                            >
                                <Save size={20} />
                                {isSubmitting ? 'Updating...' : 'Save Configuration'}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
