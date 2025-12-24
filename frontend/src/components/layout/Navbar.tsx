import React from 'react';
import { MagnifyingGlassIcon, BellIcon, Bars3Icon, UserIcon, Cog6ToothIcon, ArrowRightOnRectangleIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { useTheme } from "../theme-provider";
import { useAuth } from "../../context/AuthContext";

interface NavbarProps {
    onMobileMenuToggle?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMobileMenuToggle }) => {
    const { theme, setTheme } = useTheme();
    const { user, logout } = useAuth();

    return (
        <header className="h-16 bg-white dark:bg-background border-b border-zinc-200 dark:border-border flex items-center justify-between px-4 sm:px-6 sticky top-0 z-20 transition-colors duration-300">
            {/* Left side - Mobile Menu Button */}
            <div className="flex items-center gap-3">
                {/* Mobile Menu Toggle - Only visible on mobile */}
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onMobileMenuToggle}
                    className="lg:hidden text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-800"
                >
                    <Bars3Icon className="h-6 w-6" />
                </Button>
            </div>

            {/* Right side - Notifications & User Profile */}
            <div className="flex items-center gap-2 ml-4">
                {/* Theme Toggle */}
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                    className="relative text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-800"
                >
                    <SunIcon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 absolute" />
                    <MoonIcon className="h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 absolute" />
                    <span className="sr-only">Toggle theme</span>
                </Button>

                <Button variant="ghost" size="icon" className="relative text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-800">
                    <BellIcon className="h-6 w-6" />
                    <span className="absolute top-2.5 right-2.5 w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                </Button>

                <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 mx-2 hidden sm:block"></div>

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <button className="flex items-center gap-2 p-1.5 rounded-full hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-all focus:outline-none ring-offset-2 focus:ring-2 focus:ring-zinc-900/10 dark:focus:ring-white/10">
                            <Avatar className="h-8 w-8 border border-zinc-200 dark:border-zinc-700">
                                <AvatarImage src={user?.avatar || 'https://ui-avatars.com/api/?name=User&background=6366f1&color=fff'} />
                                <AvatarFallback>{user?.name?.substring(0, 2).toUpperCase() || 'US'}</AvatarFallback>
                            </Avatar>
                            <div className="hidden md:block text-left">
                                <p className="text-sm font-medium text-zinc-700 dark:text-zinc-200 leading-none">{user?.name || 'Usuário'}</p>
                                <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium">{user?.role || 'Usuário'}</p>
                            </div>
                        </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56 border-zinc-200 dark:border-border text-zinc-700 dark:text-foreground bg-white dark:bg-card shadow-lg">
                        <DropdownMenuLabel className="text-zinc-900 dark:text-white">Minha Conta</DropdownMenuLabel>
                        <DropdownMenuSeparator className="bg-zinc-100 dark:bg-zinc-800" />
                        <DropdownMenuItem className="cursor-pointer gap-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-white">
                            <UserIcon className="h-4 w-4" /> <span>Meu Perfil</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-white">
                            <Cog6ToothIcon className="h-4 w-4" /> <span>Configurações</span>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator className="bg-zinc-100 dark:bg-zinc-800" />
                        <DropdownMenuItem onClick={logout} className="cursor-pointer gap-2 text-red-600 focus:text-red-700 focus:bg-red-50 dark:focus:bg-red-900/10">
                            <ArrowRightOnRectangleIcon className="h-4 w-4" /> <span>Sair</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
};
