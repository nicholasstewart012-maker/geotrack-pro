import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Gauge, Lock, Mail, Fingerprint, ChevronRight } from 'lucide-react';
import { cn } from '../lib/utils';

interface LoginViewProps {
    onLogin: (credentials: any) => void;
    isLoading: boolean;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLogin, isLoading }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onLogin({ email, password });
    };

    return (
        <div className="fixed inset-0 bg-ios-bg selection:bg-ios-blue/30 font-sans overflow-hidden flex flex-col items-center justify-center p-6">
            <div className="absolute inset-0 z-0 bg-premium bg-cover bg-center opacity-60">
                <div className="absolute inset-0 bg-ios-gradient"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-sm relative z-10"
            >
                <div className="flex flex-col items-center mb-12">
                    <motion.div
                        initial={{ y: -20 }}
                        animate={{ y: 0 }}
                        className="w-20 h-20 bg-ios-blue rounded-[24px] flex items-center justify-center shadow-2xl shadow-ios-blue/40 mb-6"
                    >
                        <Gauge className="text-white" size={44} />
                    </motion.div>
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase leading-none">GeoTrack</h1>
                    <p className="text-xs text-ios-blue font-bold tracking-[0.4em] uppercase mt-2">Enterprise</p>
                </div>

                <div className="ios-card p-8 border-white/10">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1">
                            <label className="text-[10px] font-black text-ios-secondary uppercase tracking-widest ml-1">Fleet ID / Email</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-ios-secondary" size={18} />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="admin@geotrack.pro"
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 pl-12 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] font-black text-ios-secondary uppercase tracking-widest ml-1">Master Access Key</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-ios-secondary" size={18} />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl p-4 pl-12 text-white placeholder:text-white/10 outline-none focus:bg-white/10 focus:border-ios-blue transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className={cn(
                                "w-full bg-white text-black font-black py-5 rounded-3xl shadow-2xl flex items-center justify-center gap-2 active:scale-95 transition-all mt-4",
                                isLoading && "opacity-50"
                            )}
                        >
                            {isLoading ? "Authenticating..." : "System Login"}
                            {!isLoading && <ChevronRight size={20} />}
                        </button>
                    </form>

                    <div className="mt-8 flex flex-col items-center gap-4">
                        <button className="flex items-center gap-3 text-ios-secondary active:opacity-50 transition-opacity">
                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                                <Fingerprint size={20} />
                            </div>
                            <span className="text-[10px] font-black uppercase tracking-widest">Biometric Scan</span>
                        </button>
                        <p className="text-[9px] text-white/20 font-bold uppercase tracking-[0.2em]">Authorized Personnel Only</p>
                    </div>
                </div>
            </motion.div>

            <div className="mt-12 text-center relative z-10 px-10">
                <p className="text-[10px] text-ios-secondary font-medium leading-relaxed">
                    Protecting over 40,000 assets worldwide with military-grade encryption and real-time Geotab synchronization.
                </p>
            </div>
        </div>
    );
};
