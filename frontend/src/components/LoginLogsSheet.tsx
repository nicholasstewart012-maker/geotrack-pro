import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Shield, Clock, User } from 'lucide-react';
import { cn } from '../lib/utils';

interface LoginLogsSheetProps {
    isOpen: boolean;
    onClose: () => void;
    API_BASE: string;
}

interface LoginLog {
    id: number;
    email: string;
    login_time: string;
    user_id: number;
}

export const LoginLogsSheet: React.FC<LoginLogsSheetProps> = ({
    isOpen, onClose, API_BASE
}) => {
    const [logs, setLogs] = useState<LoginLog[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchLogs();
        }
    }, [isOpen]);

    const fetchLogs = async () => {
        setIsLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE}/admin/logs/login`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setLogs(data);
            }
        } catch (err) {
            console.error("Failed to fetch login logs", err);
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }).format(date);
    };

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
                                <h2 className="text-3xl font-black text-white">Login Logs</h2>
                                <p className="text-ios-blue text-xs font-bold uppercase tracking-widest">Security Audit</p>
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
                                    <Shield className="animate-spin" size={32} />
                                    <p className="font-bold text-xs uppercase tracking-widest">Loading Records...</p>
                                </div>
                            ) : logs.length === 0 ? (
                                <div className="text-center py-20 text-ios-secondary">
                                    <p className="font-bold">No login records found</p>
                                </div>
                            ) : (
                                logs.map((log) => (
                                    <div key={log.id} className="ios-card p-4 flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-xl bg-ios-blue/10 flex items-center justify-center text-ios-blue">
                                                <User size={18} />
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-white text-sm">{log.email}</h4>
                                                <div className="flex items-center gap-1 text-ios-secondary text-[10px] font-bold uppercase mt-1">
                                                    <Clock size={10} />
                                                    <span>{formatDate(log.login_time)}</span>
                                                </div>
                                            </div>
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
