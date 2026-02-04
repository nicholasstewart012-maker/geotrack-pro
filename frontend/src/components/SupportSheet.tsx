import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageSquare, Send, Paperclip, AlertOctagon, Users, FileText } from 'lucide-react';
import { cn } from '../lib/utils';

interface SupportSheetProps {
    isOpen: boolean;
    onClose: () => void;
    API_BASE: string;
    userEmail: string;
}

export const SupportSheet: React.FC<SupportSheetProps> = ({ isOpen, onClose, API_BASE, userEmail }) => {
    const [issueType, setIssueType] = useState('');
    const [impactCount, setImpactCount] = useState('1');
    const [description, setDescription] = useState('');
    const [attachment, setAttachment] = useState<File | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('issue_type', issueType);
            formData.append('impact_count', impactCount);
            formData.append('description', description);
            formData.append('user_email', userEmail);
            if (attachment) {
                formData.append('attachment', attachment);
            }

            const res = await fetch(`${API_BASE}/support/submit`, {
                method: 'POST',
                body: formData, // Content-Type is set automatically for FormData
            });

            if (res.ok) {
                setSuccess(true);
                setTimeout(() => {
                    setSuccess(false);
                    onClose();
                    setIssueType('');
                    setDescription('');
                    setAttachment(null);
                }, 2000);
            } else {
                throw new Error('Failed to submit ticket');
            }
        } catch (err) {
            setError('Something went wrong. Please try again.');
        } finally {
            setIsSubmitting(false);
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
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed inset-x-0 bottom-0 h-[85vh] bg-[#1c1c1e] rounded-t-[32px] overflow-hidden z-50 flex flex-col"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between px-6 py-5 border-b border-white/10 bg-[#1c1c1e] shrink-0">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <MessageSquare className="text-ios-blue" />
                                Support
                            </h2>
                            <button
                                onClick={onClose}
                                className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors"
                            >
                                <X size={20} className="text-white" />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6">
                            {success ? (
                                <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                                    <div className="w-16 h-16 rounded-full bg-ios-green/20 flex items-center justify-center">
                                        <Send className="text-ios-green" size={32} />
                                    </div>
                                    <h3 className="text-2xl font-bold text-white">Ticket Sent!</h3>
                                    <p className="text-ios-secondary">We'll get back to you shortly at {userEmail}.</p>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    {error && (
                                        <div className="p-4 bg-red-500/20 text-red-400 rounded-xl text-sm font-medium border border-red-500/30">
                                            {error}
                                        </div>
                                    )}

                                    {/* Issue Type */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-ios-secondary uppercase tracking-wider flex items-center gap-2">
                                            <AlertOctagon size={14} /> Current Issue
                                        </label>
                                        <input
                                            type="text"
                                            value={issueType}
                                            onChange={(e) => setIssueType(e.target.value)}
                                            placeholder="e.g. Map not loading..."
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-ios-blue focus:ring-1 focus:ring-ios-blue transition-all"
                                            required
                                        />
                                    </div>

                                    {/* Impact Count */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-ios-secondary uppercase tracking-wider flex items-center gap-2">
                                            <Users size={14} /> How many people are affected?
                                        </label>
                                        <div className="grid grid-cols-2 gap-3">
                                            {['1', '2-5', '6-10', 'All'].map((val) => (
                                                <button
                                                    key={val}
                                                    type="button"
                                                    onClick={() => setImpactCount(val)}
                                                    className={cn(
                                                        "px-4 py-3 rounded-xl text-sm font-bold border transition-all",
                                                        impactCount === val
                                                            ? "bg-ios-blue border-ios-blue text-white"
                                                            : "bg-black/40 border-white/10 text-ios-secondary hover:border-white/30"
                                                    )}
                                                >
                                                    {val}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Description */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-ios-secondary uppercase tracking-wider flex items-center gap-2">
                                            <FileText size={14} /> Description
                                        </label>
                                        <textarea
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            placeholder="Please describe the issue in detail..."
                                            rows={5}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-ios-blue focus:ring-1 focus:ring-ios-blue transition-all resize-none"
                                            required
                                        />
                                    </div>

                                    {/* Attachment */}
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-ios-secondary uppercase tracking-wider flex items-center gap-2">
                                            <Paperclip size={14} /> Attachments (Optional)
                                        </label>
                                        <div className="relative">
                                            <input
                                                type="file"
                                                id="file-upload"
                                                onChange={(e) => setAttachment(e.target.files?.[0] || null)}
                                                className="hidden"
                                            />
                                            <label
                                                htmlFor="file-upload"
                                                className="flex items-center justify-center w-full px-4 py-4 border-2 border-dashed border-white/10 rounded-xl cursor-pointer hover:border-white/30 hover:bg-white/5 transition-all group"
                                            >
                                                <div className="text-center">
                                                    {attachment ? (
                                                        <span className="text-ios-blue font-semibold break-all">
                                                            {attachment.name}
                                                        </span>
                                                    ) : (
                                                        <span className="text-ios-secondary group-hover:text-white transition-colors">
                                                            Click to upload a screenshot or log
                                                        </span>
                                                    )}
                                                </div>
                                            </label>
                                        </div>
                                    </div>
                                </form>
                            )}
                        </div>

                        {/* Footer */}
                        {!success && (
                            <div className="p-6 border-t border-white/10 bg-[#1c1c1e] shrink-0">
                                <button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || !issueType || !description}
                                    className="w-full bg-ios-blue hover:bg-ios-blue/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                                >
                                    {isSubmitting ? (
                                        <motion.div
                                            animate={{ rotate: 360 }}
                                            transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                                            className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                                        />
                                    ) : (
                                        <>
                                            Submit Ticket <Send size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        )}
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
