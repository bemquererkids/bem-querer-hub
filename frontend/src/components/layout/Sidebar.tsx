import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    MessageSquare,
    Users,
    Settings,
    LayoutDashboard,
    Calendar as CalendarIcon,
    ChevronLeft,
    ChevronRight,
    Search,
} from 'lucide-react';
import clsx from 'clsx';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';

export type ViewType = 'dashboard' | 'chat' | 'crm' | 'followup' | 'prompt-config' | 'clinic-config' | 'settings';

interface SidebarProps {
    currentView: ViewType;
    setCurrentView: (view: ViewType) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, setCurrentView }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    const navItems = [
        { id: 'dashboard' as ViewType, icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'crm' as ViewType, icon: Users, label: 'CRM' },
        { id: 'chat' as ViewType, icon: MessageSquare, label: 'Chat', badge: '80' },
        { id: 'followup' as ViewType, icon: CalendarIcon, label: 'Follow-up' },
    ];

    const configItems = [
        { id: 'prompt-config' as ViewType, icon: Settings, label: 'Configurar Prompt' },
        { id: 'clinic-config' as ViewType, icon: Settings, label: 'Clínica' },
    ];

    const NavItem = ({ id, icon: Icon, label, badge }: { id: ViewType; icon: any; label: string; badge?: string }) => {
        const isActive = currentView === id;

        const content = (
            <button
                onClick={() => setCurrentView(id)}
                className={clsx(
                    "w-full flex items-center transition-all rounded-lg group relative",
                    isCollapsed ? "justify-center p-2" : "gap-3 px-3 py-2",
                    isActive
                        ? "text-white bg-gray-800 shadow-md"
                        : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                )}
            >
                <Icon className={clsx(
                    "shrink-0",
                    isCollapsed ? "w-6 h-6" : "w-5 h-5",
                    isActive ? "text-cyan-400" : "text-gray-400 group-hover:text-white"
                )} />

                {!isCollapsed && (
                    <>
                        <span className="flex-1 text-left text-sm font-medium truncate">{label}</span>
                        {badge && (
                            <span className="bg-cyan-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                                {badge}
                            </span>
                        )}
                    </>
                )}
            </button>
        );

        if (isCollapsed) {
            return (
                <Tooltip delayDuration={0}>
                    <TooltipTrigger asChild>
                        {content}
                    </TooltipTrigger>
                    <TooltipContent side="right" className="bg-gray-900 border border-gray-800">
                        {label} {badge && `(${badge})`}
                    </TooltipContent>
                </Tooltip>
            );
        }

        return content;
    };

    return (
        <TooltipProvider>
            <motion.aside
                initial={false}
                animate={{ width: isCollapsed ? 80 : 256 }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                className="h-screen bg-gray-950 flex flex-col shadow-2xl z-30 relative border-r border-gray-800"
            >
                {/* Logo Header */}
                <div className={clsx(
                    "h-16 flex items-center border-b border-gray-800 shrink-0",
                    isCollapsed ? "justify-center px-0" : "px-4 gap-3"
                )}>
                    <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-teal-500 rounded-lg flex items-center justify-center text-white text-lg shadow-lg shrink-0">
                        🦷
                    </div>
                    {!isCollapsed && (
                        <span className="font-bold text-white text-lg tracking-tight truncate animate-in fade-in slide-in-from-left-2 duration-300">
                            Bem-Querer
                        </span>
                    )}
                </div>

                {/* Toggle Button */}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="absolute -right-3 top-20 w-6 h-6 bg-gray-800 border border-gray-700 rounded-full flex items-center justify-center text-gray-400 hover:text-white shadow-lg z-40 transition-colors"
                >
                    {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                </button>

                {/* Search / Context */}
                {!isCollapsed && (
                    <div className="p-4 shrink-0">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                            <input
                                type="text"
                                placeholder="Buscar..."
                                className="w-full bg-gray-900/50 text-white placeholder-gray-500 pl-10 pr-4 py-2 rounded-lg text-sm border border-gray-800 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/10 transition-all"
                            />
                        </div>
                    </div>
                )}
                {isCollapsed && (
                    <div className="flex justify-center p-4">
                        <Search className="w-5 h-5 text-gray-500" />
                    </div>
                )}

                {/* Navigation Items */}
                <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-hide">
                    {/* Main Menu */}
                    <div>
                        {!isCollapsed && (
                            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-3 mb-3">Principal</p>
                        )}
                        <div className="space-y-1">
                            {navItems.map(item => (
                                <NavItem key={item.id} {...item} />
                            ))}
                        </div>
                    </div>

                    {/* Settings Menu */}
                    <div>
                        {!isCollapsed && (
                            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest px-3 mb-3">Configurações</p>
                        )}
                        <div className="space-y-1">
                            {configItems.map(item => (
                                <NavItem key={item.id} {...item} />
                            ))}
                        </div>
                    </div>
                </nav>

                {/* User Profile (Bottom) */}
                <div className="p-4 border-t border-gray-800 bg-gray-950/50">
                    <div className={clsx(
                        "flex items-center gap-3 cursor-pointer hover:bg-gray-800/50 p-2 rounded-lg transition-all",
                        isCollapsed ? "justify-center" : ""
                    )}>
                        <Avatar className="w-9 h-9 border-2 border-gray-800 shrink-0">
                            <AvatarImage src="https://ui-avatars.com/api/?name=Ana+Silva&background=00ACC1&color=fff" />
                            <AvatarFallback>AS</AvatarFallback>
                        </Avatar>
                        {!isCollapsed && (
                            <div className="flex-1 min-w-0 animate-in fade-in slide-in-from-left-2 duration-300">
                                <p className="text-sm font-medium text-white truncate">Dra. Ana Silva</p>
                                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider truncate">Dentista Admin</p>
                            </div>
                        )}
                    </div>
                </div>
            </motion.aside>
        </TooltipProvider>
    );
};
