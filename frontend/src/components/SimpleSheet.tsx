import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bell, User } from 'lucide-react';

interface SimpleSheetProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    icon: React.ElementType;
    description: string;
}

export const SimpleSheet: React.FC<SimpleSheetProps> = ({
    isOpen, onClose, title, icon: Icon, description
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

                        <div className="flex justify-between items-center mb-8 px-1">
                            <h2 className="text-3xl font-black text-white">{title}</h2>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 bg-white/5 rounded-full flex items-center justify-center text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex flex-col items-center justify-center py-10 space-y-6 text-center">
                            <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center text-ios-secondary">
                                <Icon size={40} />
                            </div>
                            <div className="space-y-2">
                                <p className="text-white font-bold text-xl">{title} Coming Soon</p>
                                <p className="text-ios-secondary text-sm px-10">{description}</p>
                            </div>

                            <button
                                onClick={onClose}
                                className="w-full bg-white text-black font-black py-5 rounded-3xl shadow-xl active:scale-[0.98] transition-all mt-4"
                            >
                                Got it
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
