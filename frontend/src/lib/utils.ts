import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export const formatMileage = (miles: number) => {
    return new Intl.NumberFormat('en-US').format(Math.round(miles));
};

export const getStatusColor = (mileage: number) => {
    if (mileage < 250) return 'text-red-500 bg-red-50 border-red-100';
    if (mileage < 1000) return 'text-amber-500 bg-amber-50 border-amber-100';
    return 'text-emerald-500 bg-emerald-50 border-emerald-100';
};
