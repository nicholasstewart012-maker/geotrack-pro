import React from 'react';
import { motion } from 'framer-motion';

export const VehicleSkeleton = () => {
    return (
        <div className="ios-card overflow-hidden animate-pulse">
            <div className="p-5 space-y-4">
                <div className="flex justify-between items-start">
                    <div className="space-y-2">
                        <div className="h-6 w-32 bg-white/5 rounded-md" />
                        <div className="h-4 w-20 bg-white/5 rounded-sm" />
                    </div>
                    <div className="h-6 w-16 bg-white/5 rounded-xl border border-white/5" />
                </div>

                <div className="flex gap-3">
                    <div className="flex-1 bg-white/5 p-4 rounded-3xl border border-white/5 h-20" />
                    <div className="flex-1 bg-white/5 p-4 rounded-3xl border border-white/5 h-20" />
                </div>

                <div className="space-y-3 pt-2">
                    <div className="flex justify-between items-center h-3 w-3/4 bg-white/5 rounded" />
                    <div className="h-2.5 w-full bg-white/10 rounded-full border border-white/5" />
                </div>
            </div>

            <div className="grid grid-cols-2 border-t border-white/5 divide-x divide-white/5">
                <div className="h-12 bg-white/5" />
                <div className="h-12 bg-white/5" />
            </div>
        </div>
    );
};
