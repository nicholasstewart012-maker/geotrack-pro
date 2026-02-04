import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Settings, BarChart3, Truck,
    Plus, Gauge, RefreshCw, User, Mail, ChevronRight, Shield
} from 'lucide-react';
import { cn } from './lib/utils';
import { VehicleCard } from './components/VehicleCard';
import { EnrollmentSheet } from './components/EnrollmentSheet';
import { ConfigSheet } from './components/ConfigSheet';
import { LogSheet } from './components/LogSheet';
import { SimpleSheet } from './components/SimpleSheet';
import { VehicleSkeleton } from './components/VehicleSkeleton';
import { HistorySheet } from './components/HistorySheet';
import { LineChart } from './components/LineChart';
import { LoginView } from './components/LoginView';
import { ProfileSheet } from './components/ProfileSheet';
import { SecuritySheet } from './components/SecuritySheet';
import { PreferencesSheet } from './components/PreferencesSheet';

const getApiBase = () => {
    // If we provided an explicit API URL in environment variables
    if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;

    // In production (Vercel), we want to use the relative /api path
    // which will be rewritten to the backend function
    if (import.meta.env.PROD || window.location.hostname !== 'localhost') {
        return 'https://geotrack-pro.vercel.app/api';
    }

    // Default to local backend for development
    return 'http://localhost:8000';
};

const API_BASE = getApiBase();
console.log('API Base URL:', API_BASE);

interface Vehicle {
    id: number;
    geotab_id: string;
    name: string;
    vin?: string;
    current_mileage: number;
    current_hours: number;
    last_sync: string;
}

const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [activeTab, setActiveTab] = useState('fleet');
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [showAddVehicle, setShowAddVehicle] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [showNotifications, setShowNotifications] = useState(false);
    const [showSupport, setShowSupport] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [showProfile, setShowProfile] = useState(false);
    const [showSecurity, setShowSecurity] = useState(false);
    const [showPreferences, setShowPreferences] = useState(false);
    const [user, setUser] = useState({ email: 'admin@geotrack.pro', full_name: 'Fleet Manager' });
    const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [newVehicle, setNewVehicle] = useState({ name: '', geotab_id: '', vin: '' });
    const [settings, setSettings] = useState({
        geotab_server: '',
        geotab_db: '',
        geotab_user: '',
        geotab_pass: '',
        admin_email: ''
    });
    const [stats, setStats] = useState({ total_maintenance_cost: 0, count: 0 });

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            fetchUser(); // Fetch user details immediately
        }
        fetchVehicles();
        fetchSettings();
        fetchStats();
    }, []);

    const fetchUser = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch(`${API_BASE}/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const userData = await res.json();
                setUser(userData);
            } else {
                // If token invalid, maybe logout? For now just ignore
                console.error("Failed to fetch user profile");
            }
        } catch (err) {
            console.error("Error fetching user", err);
        }
    };

    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_BASE}/analytics/cost`);
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (err) {
            console.error("Failed to fetch stats", err);
        }
    };

    const fetchSettings = async () => {
        try {
            const res = await fetch(`${API_BASE}/settings/all`); // Need to add this endpoint or handle dict
            if (res.ok) {
                const data = await res.json();
                setSettings(prev => ({ ...prev, ...data }));
            }
        } catch (err) {
            console.error("Failed to fetch settings", err);
        }
    };

    const fetchVehicles = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/vehicles`);
            if (!res.ok) throw new Error("Backend unreachable");
            const data = await res.json();
            setVehicles(data);
        } catch (err) {
            console.error("Failed to fetch vehicles", err);
        } finally {
            setTimeout(() => setIsLoading(false), 800); // Slight delay for smoothness
        }
    };

    const handleAddVehicle = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const response = await fetch(`${API_BASE}/vehicles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newVehicle),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to register vehicle");
            }

            setShowAddVehicle(false);
            setNewVehicle({ name: '', geotab_id: '', vin: '' });
            fetchVehicles();
        } catch (err: any) {
            console.error("Failed to add vehicle:", err);
            alert(err.message || "Registration failed. Ensure backend is running.");
        } finally {
            setIsSubmitting(false);
        }
    };


    const handleDeleteVehicle = async (vehicleId: number) => {
        if (!confirm("Are you sure you want to delete this vehicle? This will also remove all logs.")) return;

        setIsSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            const headers: any = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const response = await fetch(`${API_BASE}/vehicles/${vehicleId}`, {
                method: 'DELETE',
                headers: headers,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to delete vehicle");
            }

            setVehicles(prev => prev.filter(v => v.id !== vehicleId));
            setSelectedVehicle(null);
        } catch (err: any) {
            console.error("Delete failed:", err);
            alert(err.message || "Failed to delete vehicle.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleSaveSettings = async (updatedSettings: any) => {
        setIsSubmitting(true);
        try {
            const response = await fetch(`${API_BASE}/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedSettings),
            });
            if (response.ok) {
                setSettings(updatedSettings);
                setShowSettings(false);
            }
        } catch (err) {
            console.error("Failed to save settings", err);
            alert("Connection error while saving settings.");
        } finally {
            setIsSubmitting(false);
        }
    };
    const handleLogin = async (credentials: any) => {
        setIsSubmitting(true);
        try {
            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Login failed");
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            setIsAuthenticated(true);
            fetchUser(); // Fetch user details
            fetchVehicles();
            fetchSettings();
        } catch (err: any) {
            console.error("Login error:", err);
            alert(err.message || "Invalid email or password.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleLogMaintenance = async (logData: any) => {
        setIsSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            const headers: any = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const response = await fetch(`${API_BASE}/logs`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(logData),
            });

            if (response.ok) {
                setSelectedVehicle(null);
                fetchVehicles();
            } else {
                const errData = await response.json();
                console.error("Log failed:", errData);
                const errorMsg = typeof errData.detail === 'object'
                    ? JSON.stringify(errData.detail, null, 2)
                    : errData.detail || "Unknown error";
                alert(`Failed to save log:\n${errorMsg}`);
            }
        } catch (err) {
            console.error("Failed to log maintenance", err);
            alert("Error saving log. Check console.");
        } finally {
            setIsSubmitting(false);
        }
    };
    const tabs = [
        { id: 'fleet', icon: Truck, label: 'Fleet' },
        { id: 'analytics', icon: BarChart3, label: 'Stats' },
        { id: 'settings', icon: Settings, label: 'More' },
    ];

    if (!isAuthenticated) {
        return <LoginView onLogin={handleLogin} isLoading={isSubmitting} />;
    }

    return (
        <div className="fixed inset-0 bg-ios-bg selection:bg-ios-blue/30 font-sans overflow-hidden flex flex-col items-center">
            <div className="absolute inset-0 z-0 bg-premium bg-cover bg-center">
                <div className="absolute inset-0 bg-ios-gradient"></div>
            </div>

            <div className="w-full max-w-lg h-full relative z-10 flex flex-col">
                <div className="h-12 w-full"></div>

                <header className="px-6 py-4 flex items-center justify-between">
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-ios-blue rounded-xl flex items-center justify-center shadow-lg shadow-ios-blue/20">
                            <Gauge className="text-white" size={24} />
                        </div>
                        <div>
                            <h1 className="text-lg font-black tracking-tight text-white uppercase leading-none">GeoTrack</h1>
                            <p className="text-[9px] text-ios-blue font-bold tracking-[0.2em] uppercase mt-1">Enterprise</p>
                        </div>
                    </motion.div>
                    <div className="flex gap-2">
                        <button onClick={fetchVehicles} className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90 transition-all">
                            <RefreshCw size={18} />
                        </button>
                        <button
                            onClick={() => setShowProfile(true)}
                            className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white active:scale-90 transition-all"
                        >
                            <User size={18} />
                        </button>
                    </div>
                </header>

                <main className="flex-1 px-6 pb-28 overflow-y-auto no-scrollbar pt-2">
                    <AnimatePresence mode="wait">
                        {activeTab === 'fleet' && (
                            <motion.div key="fleet" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                                <div className="flex items-end justify-between px-1">
                                    <div>
                                        <h2 className="text-3xl font-black text-white">Maintenance</h2>
                                        <p className="text-ios-secondary text-sm font-medium">{vehicles.length} Assets Online</p>
                                    </div>
                                    <button
                                        onClick={() => setShowAddVehicle(true)}
                                        className="w-14 h-14 bg-ios-blue text-white rounded-2xl flex items-center justify-center shadow-xl shadow-ios-blue/20 active:scale-90 transition-all"
                                    >
                                        <Plus size={32} />
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    {isLoading ? (
                                        <>
                                            <VehicleSkeleton />
                                            <VehicleSkeleton />
                                            <VehicleSkeleton />
                                        </>
                                    ) : (
                                        vehicles.map((v, i) => (
                                            <VehicleCard
                                                key={v.id}
                                                vehicle={v}
                                                index={i}
                                                onLogClick={() => setSelectedVehicle(v)}
                                                onHistoryClick={() => {
                                                    setSelectedVehicle(v);
                                                    setShowHistory(true);
                                                }}
                                                onDelete={() => handleDeleteVehicle(v.id)}
                                            />
                                        ))
                                    )}
                                </div>
                            </motion.div>
                        )}

                        {activeTab === 'analytics' && (
                            <motion.div key="stats" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                                <h2 className="text-3xl font-black text-white px-1 font-sans">Statistics</h2>

                                {/* Performance Ring */}
                                <div className="ios-card p-10 flex flex-col items-center gap-4 text-center">
                                    <div className="w-32 h-32 rounded-full border-[8px] border-white/5 flex items-center justify-center relative">
                                        <svg className="absolute inset-0 w-full h-full -rotate-90">
                                            <circle cx="64" cy="64" r="56" fill="transparent" stroke="rgba(10, 132, 255, 0.4)" strokeWidth="8" />
                                            <circle cx="64" cy="64" r="56" fill="transparent" stroke="#0A84FF" strokeWidth="8" strokeDasharray="351.8" strokeDashoffset="50" strokeLinecap="round" />
                                        </svg>
                                        <h3 className="text-4xl font-black text-white">88<span className="text-lg text-ios-secondary">%</span></h3>
                                    </div>
                                    <div>
                                        <p className="text-xs font-black text-ios-secondary uppercase tracking-[0.1em]">Core Health Index</p>
                                    </div>
                                </div>

                                {/* Real SVG Chart */}
                                <div className="ios-card p-6 space-y-6">
                                    <div className="flex justify-between items-start">
                                        <p className="text-[10px] font-black text-ios-secondary uppercase tracking-widest">Maintenance Cost Trend</p>
                                        <span className="text-ios-blue text-[10px] font-black">+12% vs LY</span>
                                    </div>
                                    <div className="h-40 w-full">
                                        <LineChart
                                            data={[450, 380, 520, 410, 680, 590, 720, 640]}
                                            labels={['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']}
                                        />
                                    </div>
                                    <div className="flex justify-between text-[8px] font-black text-ios-secondary uppercase px-4">
                                        <span>Jan</span>
                                        <span>Apr</span>
                                        <span>Jul</span>
                                        <span>Dec</span>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="ios-card p-6 border-l-4 border-l-ios-amber/50">
                                        <p className="text-[10px] font-black text-ios-secondary uppercase tracking-widest mb-1">Maint. Cost</p>
                                        <h4 className="text-2xl font-black text-white">${stats.total_maintenance_cost.toLocaleString()}</h4>
                                    </div>
                                    <div className="ios-card p-6 border-l-4 border-l-ios-green/50">
                                        <p className="text-[10px] font-black text-ios-secondary uppercase tracking-widest mb-1">Total Logs</p>
                                        <h4 className="text-3xl font-black text-white">{stats.count}</h4>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        <motion.div key="settings" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                            <button
                                onClick={() => setShowProfile(true)}
                                className="w-full ios-card p-5 group flex items-center justify-between active:bg-white/5 transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-2xl bg-ios-blue/10 flex items-center justify-center text-ios-blue group-active:scale-95 transition-transform">
                                        <User size={20} />
                                    </div>
                                    <div className="text-left">
                                        <p className="text-xs font-black text-white uppercase tracking-wider">User Profile</p>
                                        <p className="text-[10px] text-ios-secondary font-bold uppercase tracking-widest">{user.email}</p>
                                    </div>
                                </div>
                                <ChevronRight size={16} className="text-white/20 group-hover:text-white/40 transition-colors" />
                            </button>

                            <div className="ios-card p-2 overflow-hidden">
                                {['Notifications', 'Configurations', 'Support'].map((item, idx) => (
                                    <button
                                        key={item}
                                        onClick={() => {
                                            if (item === 'Configurations') setShowSettings(true);
                                            if (item === 'Notifications') setShowNotifications(true);
                                            if (item === 'Support') setShowSupport(true);
                                        }}
                                        className={cn(
                                            "w-full p-5 flex items-center justify-between tap-highlight-none active:bg-white/5 transition-colors",
                                            idx < 2 && "border-b border-white/5"
                                        )}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={cn(
                                                "w-10 h-10 rounded-xl flex items-center justify-center",
                                                item === 'Notifications' && "bg-ios-blue/10 text-ios-blue",
                                                item === 'Configurations' && "bg-ios-amber/10 text-ios-amber",
                                                item === 'Support' && "bg-ios-secondary/10 text-ios-secondary"
                                            )}>
                                                {item === 'Notifications' && <Mail size={20} />}
                                                {item === 'Configurations' && <Settings size={20} />}
                                                {item === 'Support' && <User size={20} />}
                                            </div>
                                            <span className="font-bold text-white">{item}</span>
                                        </div>
                                        <ChevronRight className="text-ios-secondary/50" size={20} />
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </main>

                <footer className="h-24 w-full ios-nav-blur flex justify-around items-center px-6 pb-6 pt-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn("flex flex-col items-center gap-1", activeTab === tab.id ? "text-ios-blue" : "text-ios-secondary")}
                        >
                            <tab.icon size={24} strokeWidth={activeTab === tab.id ? 2.5 : 2} />
                            <span className="text-[9px] font-black uppercase tracking-tighter">{tab.label}</span>
                        </button>
                    ))}
                </footer>
            </div>

            <ProfileSheet
                isOpen={showProfile}
                onClose={() => setShowProfile(false)}
                onLogout={() => {
                    localStorage.removeItem('token');
                    setIsAuthenticated(false);
                    setShowProfile(false);
                }}
                onSecurityClick={() => {
                    setShowProfile(false);
                    setShowSecurity(true);
                }}
                onPreferencesClick={() => {
                    setShowProfile(false);
                    setShowPreferences(true);
                }}
                user={user}
            />

            <SecuritySheet
                isOpen={showSecurity}
                onClose={() => setShowSecurity(false)}
                API_BASE={API_BASE}
            />

            <PreferencesSheet
                isOpen={showPreferences}
                onClose={() => setShowPreferences(false)}
            />

            <EnrollmentSheet
                isOpen={showAddVehicle}
                onClose={() => setShowAddVehicle(false)}
                onSubmit={handleAddVehicle}
                newVehicle={newVehicle}
                setNewVehicle={setNewVehicle}
                isSubmitting={isSubmitting}
            />

            <ConfigSheet
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
                settings={settings}
                onSave={handleSaveSettings}
                isSubmitting={isSubmitting}
            />

            <LogSheet
                isOpen={!!selectedVehicle && !showHistory}
                onClose={() => setSelectedVehicle(null)}
                vehicle={selectedVehicle}
                onSubmit={handleLogMaintenance}
                isSubmitting={isSubmitting}
            />

            <HistorySheet
                isOpen={showHistory}
                onClose={() => {
                    setShowHistory(false);
                    setSelectedVehicle(null);
                }}
                vehicle={selectedVehicle}
                API_BASE={API_BASE}
            />

            <SimpleSheet
                isOpen={showNotifications}
                onClose={() => setShowNotifications(false)}
                title="Notifications"
                icon={Mail}
                description="We're building a real-time alert engine to keep you informed of critical fleet events. Coming soon!"
            />

            <SimpleSheet
                isOpen={showSupport}
                onClose={() => setShowSupport(false)}
                title="Support"
                icon={User}
                description="Need help? Our enterprise support team is just a tap away. Implementation in progress."
            />

            <SimpleSheet
                isOpen={showSecurity}
                onClose={() => setShowSecurity(false)}
                title="Security"
                icon={Shield}
                description="Enhanced security controls including Two-Factor Authentication and API key management are coming in the next update."
            />

            <SimpleSheet
                isOpen={showPreferences}
                onClose={() => setShowPreferences(false)}
                title="Preferences"
                icon={Settings}
                description="Customize your dashboard experience, notification frequency, and theme settings here soon."
            />
        </div>
    );
};

export default App;
