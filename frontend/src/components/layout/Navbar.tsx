import React from 'react';
import { Search, Bell, Menu, User, Settings as SettingsIcon, LogOut } from 'lucide-react';
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

export const Navbar: React.FC = () => {
    return (
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sticky top-0 z-20">
            {/* Left side - Mobile Menu Toggle (future) & Search */}
            <div className="flex items-center flex-1 max-w-xl">
                <Button variant="ghost" size="icon" className="md:hidden mr-2">
                    <Menu className="h-5 w-5" />
                </Button>
                <div className="relative w-full group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-cyan-500 transition-colors" />
                    <input
                        type="text"
                        placeholder="Pesquisar em todo o Hub..."
                        className="w-full bg-gray-50 border-gray-200 pl-10 pr-4 py-2 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500/10 focus:border-cyan-500/50 transition-all outline-none"
                    />
                </div>
            </div>

            {/* Right side - Notifications & User Profile */}
            <div className="flex items-center gap-2 ml-4">
                <Button variant="ghost" size="icon" className="relative text-gray-500 hover:text-cyan-600">
                    <Bell className="h-5 w-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                </Button>

                <div className="h-8 w-px bg-gray-200 mx-2 hidden sm:block"></div>

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <button className="flex items-center gap-2 p-1 rounded-full hover:bg-gray-100 transition-all focus:outline-none">
                            <Avatar className="h-8 w-8 border border-gray-200">
                                <AvatarImage src="https://ui-avatars.com/api/?name=Ana+Silva&background=00ACC1&color=fff" />
                                <AvatarFallback>AS</AvatarFallback>
                            </Avatar>
                            <div className="hidden md:block text-left">
                                <p className="text-xs font-semibold text-gray-900 leading-none">Dra. Ana Silva</p>
                                <p className="text-[10px] text-gray-500 mt-0.5">Administrador</p>
                            </div>
                        </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuLabel>Minha Conta</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="cursor-pointer gap-2">
                            <User className="h-4 w-4" /> <span>Meu Perfil</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer gap-2">
                            <SettingsIcon className="h-4 w-4" /> <span>Configurações</span>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="cursor-pointer gap-2 text-red-600 focus:text-red-600">
                            <LogOut className="h-4 w-4" /> <span>Sair</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
};
