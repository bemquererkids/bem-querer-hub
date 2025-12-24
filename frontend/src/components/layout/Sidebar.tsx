import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import {
    ChatBubbleLeftRightIcon,
    UserGroupIcon,
    Cog6ToothIcon,
    Squares2X2Icon,
    CalendarIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    BuildingOfficeIcon,
    UserPlusIcon,
    CubeIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';

export type ViewType = 'dashboard' | 'chat' | 'crm' | 'followup' | 'prompt-config' | 'clinic-config' | 'invite-management' | 'modules-settings' | 'settings';

interface SidebarProps {
    currentView: ViewType;
    setCurrentView: (view: ViewType) => void;
    isMobileMenuOpen: boolean;
    setIsMobileMenuOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, setCurrentView, isMobileMenuOpen, setIsMobileMenuOpen }) => {
    const { user } = useAuth();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const navItems = [
        { id: 'dashboard' as ViewType, icon: Squares2X2Icon, label: 'Dashboard' },
        { id: 'chat' as ViewType, icon: ChatBubbleLeftRightIcon, label: 'Chat', badge: '80' },
        { id: 'crm' as ViewType, icon: UserGroupIcon, label: 'CRM' },
        { id: 'followup' as ViewType, icon: CalendarIcon, label: 'Follow-up' },
    ];

    const configItems = [
        { id: 'prompt-config' as ViewType, icon: Cog6ToothIcon, label: 'Configurar Prompt' },
        { id: 'clinic-config' as ViewType, icon: BuildingOfficeIcon, label: 'Clínica' },
        { id: 'modules-settings' as ViewType, icon: CubeIcon, label: 'Módulos' },
        { id: 'invite-management' as ViewType, icon: UserPlusIcon, label: 'Gerenciar Acessos' },
        { id: 'settings' as ViewType, icon: Cog6ToothIcon, label: 'Configurações' },
    ];

    const handleNavClick = (id: ViewType) => {
        setCurrentView(id);
        setIsMobileMenuOpen(false); // Close mobile menu after navigation
    };

    const NavItem = ({ id, icon: Icon, label, badge }: { id: ViewType; icon: any; label: string; badge?: string }) => {
        const isActive = currentView === id;

        const content = (
            <button
                onClick={() => handleNavClick(id)}
                className={clsx(
                    "w-full flex items-center transition-all rounded-md group relative",
                    isCollapsed ? "justify-center p-2" : "gap-3 px-3 py-2",
                    isActive
                        ? "text-indigo-600 bg-indigo-50 shadow-sm ring-1 ring-indigo-100 dark:bg-primary/10 dark:text-primary dark:ring-primary/20"
                        : "text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50/80 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-white/5"
                )}
            >
                <Icon className={clsx(
                    "shrink-0",
                    isCollapsed ? "w-5 h-5" : "w-5 h-5"
                )} />

                {!isCollapsed && (
                    <>
                        <span className="flex-1 text-left text-sm font-medium truncate">{label}</span>
                        {badge && (
                            <span className={clsx(
                                "px-2 py-0.5 text-[10px] font-bold rounded-full",
                                isActive
                                    ? "bg-indigo-600 text-white dark:bg-primary dark:text-primary-foreground"
                                    : "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                            )}>
                                {badge}
                            </span>
                        )}
                    </>
                )}
            </button>
        );

        if (isCollapsed) {
            return (
                <TooltipProvider>
                    <Tooltip delayDuration={0}>
                        <TooltipTrigger asChild>
                            {content}
                        </TooltipTrigger>
                        <TooltipContent side="right" className="bg-white border-zinc-200 text-zinc-900 shadow-md dark:bg-zinc-900 dark:text-white dark:border-zinc-800">
                            {label}
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );
        }

        return content;
    };

    return (
        <>
            {/* Mobile Menu Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <motion.aside
                initial={false}
                animate={{ width: isCollapsed ? 72 : 240 }}
                transition={{ duration: 0.2, ease: 'easeInOut' }}
                className={clsx(
                    "h-screen bg-white dark:bg-background flex flex-col z-50 relative border-r border-zinc-200 dark:border-border shadow-sm transition-colors duration-300",
                    // Mobile: fixed position, slide in from left
                    "fixed lg:relative",
                    isMobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
                    "transition-transform duration-300 ease-in-out"
                )}
            >
                {/* Logo Header */}
                <div className={clsx(
                    "h-16 flex items-center shrink-0 transition-all border-b border-zinc-100/50 dark:border-zinc-800/50",
                    isCollapsed ? "justify-center px-0" : "px-6 gap-3"
                )}>
                    {isCollapsed ? (
                        <div className="w-8 h-8 bg-indigo-600 dark:bg-primary rounded-md flex items-center justify-center text-white font-bold text-lg shadow-sm">
                            N
                        </div>
                    ) : (
                        <div className="flex items-center gap-2">
                            <div className="w-6 h-6 bg-indigo-600 dark:bg-primary rounded flex items-center justify-center shrink-0">
                                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <span className="font-bold text-zinc-900 dark:text-white text-lg tracking-wide animate-in fade-in">
                                NEXUS
                            </span>
                        </div>
                    )}
                </div>

                {/* Toggle Button */}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="absolute -right-3 top-20 w-6 h-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-full flex items-center justify-center text-zinc-400 hover:text-zinc-600 dark:hover:text-white shadow-md z-40 transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-800"
                >
                    {isCollapsed ? <ChevronRightIcon className="w-3 h-3" /> : <ChevronLeftIcon className="w-3 h-3" />}
                </button>

                {/* Navigation Items */}
                <nav className="flex-1 overflow-y-auto px-3 py-6 space-y-8 scrollbar-hide">
                    {/* Main Menu */}
                    <div>
                        {!isCollapsed && (
                            <p className="text-[11px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider px-3 mb-2">Plataforma</p>
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
                            <p className="text-[11px] font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider px-3 mb-2">Administração</p>
                        )}
                        <div className="space-y-1">
                            {configItems.map(item => (
                                <NavItem key={item.id} {...item} />
                            ))}
                        </div>
                    </div>
                </nav>
            </motion.aside>
        </>
    );
};
