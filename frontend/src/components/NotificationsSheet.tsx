import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, CheckCircle, AlertTriangle, Info, Trash2 } from 'lucide-react';
import { cn } from '../lib/utils';
// If no UI components, I'll use raw HTML/Tailwind

interface Notification {
    id: number;
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error';
    is_read: boolean;
    created_at: string;
}

interface NotificationsSheetProps {
    isOpen: boolean;
    onClose: () => void;
    API_BASE: string;
}

export const NotificationsSheet: React.FC<NotificationsSheetProps> = ({ isOpen, onClose, API_BASE }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchNotifications();
        }
    }, [isOpen]);

    const fetchNotifications = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/notifications`);
            if (res.ok) {
                const data = await res.json();
                setNotifications(data);
            }
        } catch (error) {
            console.error("Failed to fetch notifications", error);
        } finally {
            setIsLoading(false);
        }
    };

    const markAsRead = async (id: number) => {
        try {
            await fetch(`${API_BASE}/notifications/${id}/read`, { method: 'POST' });
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
        } catch (error) {
            console.error("Failed to mark read", error);
        }
    };

    const markAllAsRead = async () => {
        try {
            await fetch(`${API_BASE}/notifications/read-all`, { method: 'POST' });
            setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        } catch (error) {
            console.error("Failed to mark all read", error);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ y: "100%" }}
                        animate={{ y: 0 }}
                        exit={{ y: "100%" }}
                        transition={{ type: "spring", damping: 25, stiffness: 200 }}
                        className="fixed bottom-0 left-0 right-0 h-[85vh] bg-ios-bg rounded-t-[2rem] z-50 flex flex-col items-center overflow-hidden"
                    >
                        {/* Desktop Constraint Helper */}
                        <div className="w-full max-w-md flex flex-col h-full bg-ios-bg relative">
                            {/* Drag Handle */}
                            <div className="w-full flex justify-center pt-3 pb-2" onClick={onClose}>
                                <div className="w-12 h-1.5 bg-white/20 rounded-full" />
                            </div>

                            {/* Header */}
                            <div className="px-6 py-4 flex justify-between items-center border-b border-white/5">
                                <div>
                                    <h2 className="text-2xl font-black text-white">Notifications</h2>
                                    <p className="text-ios-secondary text-xs font-medium">Recent alerts and updates</p>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={markAllAsRead}
                                        className="text-[10px] font-bold text-ios-blue uppercase tracking-wider px-3 py-1.5 bg-ios-blue/10 rounded-lg hover:bg-ios-blue/20 transition-colors"
                                    >
                                        Mark All Read
                                    </button>
                                    <button onClick={onClose} className="p-2 bg-white/5 hover:bg-white/10 rounded-full text-white transition-colors">
                                        <X size={20} />
                                    </button>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                {isLoading ? (
                                    <div className="flex justify-center py-10">
                                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                                    </div>
                                ) : notifications.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center h-64 text-center p-6 opacity-50">
                                        <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                                            <Mail size={32} className="text-white/30" />
                                        </div>
                                        <p className="text-white font-bold">All caught up!</p>
                                        <p className="text-sm text-ios-secondary">No new notifications</p>
                                    </div>
                                ) : (
                                    notifications.map((notif) => (
                                        <motion.div
                                            key={notif.id}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            onClick={() => !notif.is_read && markAsRead(notif.id)}
                                            className={cn(
                                                "p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group",
                                                notif.is_read ? "bg-white/5 border-transparent opacity-60" : "bg-white/10 border-ios-blue/30"
                                            )}
                                        >
                                            {/* Unread Indicator */}
                                            {!notif.is_read && (
                                                <div className="absolute top-4 right-4 w-2 h-2 bg-ios-blue rounded-full shadow-[0_0_10px_rgba(10,132,255,0.5)]"></div>
                                            )}

                                            <div className="flex gap-4">
                                                <div className={cn(
                                                    "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
                                                    notif.type === 'warning' ? "bg-ios-amber/20 text-ios-amber" :
                                                        notif.type === 'error' ? "bg-ios-red/20 text-ios-red" :
                                                            "bg-ios-blue/20 text-ios-blue"
                                                )}>
                                                    {notif.type === 'warning' ? <AlertTriangle size={20} /> :
                                                        notif.type === 'error' ? <AlertTriangle size={20} /> : // Or a different icon
                                                            <Info size={20} />}
                                                </div>
                                                <div className="flex-1">
                                                    <h4 className={cn("font-bold text-sm mb-1", notif.is_read ? "text-white/70" : "text-white")}>{notif.title}</h4>
                                                    <p className="text-xs text-ios-secondary leading-relaxed">{notif.message}</p>
                                                    <p className="text-[10px] text-white/20 mt-2 font-mono">{new Date(notif.created_at).toLocaleString()}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))
                                )}
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
