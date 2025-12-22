import { useState } from 'react';
import { LoginPage } from './components/auth/LoginPage';
import { ChatLayout } from './components/chat/ChatLayout';
import { KanbanBoard } from './components/crm/KanbanBoard';
import { IntegrationsSettings } from './components/settings/IntegrationsSettings';
import { ConfigPromptPage } from './components/settings/ConfigPromptPage';
import { DashboardHome } from './components/dashboard/DashboardHome';
import { UIElementsPage } from './components/dashboard/UIElementsPage';
import { FollowUpPage } from './components/crm/FollowUpPage';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Avatar, AvatarImage, AvatarFallback } from './components/ui/avatar';
import { 
    MessageSquare, 
    LayoutDashboard, 
    Users, 
    Settings, 
    LogOut, 
    Bell, 
    Search, 
    Menu, 
    Plus,
    ChevronDown,
    Home,
    FileText,
    PieChart,
    Layers,
    Type,
    Calendar as CalendarIcon
} from 'lucide-react';
import clsx from 'clsx';

type ViewType = 'dashboard' | 'chat' | 'crm' | 'followup' | 'prompt-config' | 'clinic-config' | 'settings';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Start as false to show Login
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  if (!isAuthenticated) {
      return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  // Template Style: Clean White Sidebar with specific styling
  const SidebarItem = ({ id, icon: Icon, label, badge, isHeader }: any) => {
      if (isHeader) {
          return <p className="px-6 text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-2 mt-6">{label}</p>;
      }
      return (
        <Button 
          variant="ghost"
          onClick={() => setCurrentView(id)}
          className={clsx(
            "w-full justify-start gap-3 px-6 h-11 text-sm font-medium transition-all rounded-none border-l-[3px]",
            currentView === id 
              ? "text-blue-600 bg-blue-50 border-blue-600" 
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 border-transparent"
          )}
        >
          <Icon className={clsx("w-4 h-4", currentView === id ? "text-blue-600" : "text-slate-400")} />
          <span>{label}</span>
          {badge && (
              <span className="ml-auto bg-green-500 text-white text-[10px] px-1.5 py-0.5 rounded font-bold shadow-sm">
                  {badge}
              </span>
          )}
        </Button>
      );
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-background font-sans">
      
      {/* 1. TOP NAVBAR (Template Style: Blue Background) */}
      <header className="h-16 bg-[#1a97d4] text-white shadow-md z-30 flex items-center justify-between px-4 lg:px-6">
         <div className="flex items-center gap-4 w-64">
            <div className="flex items-center gap-2">
                <span className="font-bold text-xl tracking-tight flex items-center gap-2">
                    <span className="text-yellow-400">🦷</span> Bem-Querer
                </span>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} className="text-white/80 hover:text-white hover:bg-white/10 lg:hidden">
                <Menu className="w-6 h-6" />
            </Button>
         </div>

         {/* Center Tabs (Template Style) */}
         <div className="hidden md:flex items-center gap-1">
             {['Agenda', 'Financeiro', 'Indicadores'].map(tab => (
                 <Button key={tab} variant="ghost" className="text-white/80 hover:text-white hover:bg-white/10 h-8 text-xs uppercase font-bold tracking-wide">
                     {tab}
                 </Button>
             ))}
         </div>

         {/* Right Actions */}
         <div className="flex items-center gap-4">
            <div className="relative cursor-pointer">
                <FileText className="w-5 h-5 text-white/80 hover:text-white" />
            </div>
            <div className="relative cursor-pointer">
                <Bell className="w-5 h-5 text-white/80 hover:text-white" />
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-[#1a97d4]"></span>
            </div>
            
            <div className="flex items-center gap-3 pl-4 ml-2 border-l border-white/20 cursor-pointer">
                <div className="text-right hidden md:block">
                    <p className="text-xs font-bold leading-none">Dra. Ana Silva</p>
                    <p className="text-xs opacity-70">Dentista Admin</p>
                </div>
                <Avatar className="w-8 h-8 border-2 border-white/50">
                    <AvatarImage src="https://ui-avatars.com/api/?name=Ana+Silva&background=333&color=fff" />
                    <AvatarFallback>AS</AvatarFallback>
                </Avatar>
            </div>
         </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        
        {/* 2. SIDEBAR (Template Style: White with Profile) */}
        <aside className={clsx(
            "w-64 bg-white shadow-xl z-20 flex flex-col transition-all duration-300 absolute lg:relative h-full border-r border-slate-100",
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0 lg:w-0 lg:overflow-hidden"
        )}>
            {/* Menu Items */}
            <nav className="flex-1 overflow-y-auto pb-4 pt-4">
                <p className="px-6 text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-2 mt-2">MENU PRINCIPAL</p>
                <SidebarItem id="dashboard" icon={Home} label="Dashboard" />
                <SidebarItem id="crm" icon={Users} label="CRM" />
                <SidebarItem id="chat" icon={MessageSquare} label="Chat" badge="80" />
                
                <SidebarItem id="followup" icon={CalendarIcon} label="Follow-up" />
                
                <p className="px-6 text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-2 mt-6">CONFIGURAÇÕES</p>
                <SidebarItem id="prompt-config" icon={Type} label="Configurar Prompt" />
                <SidebarItem id="clinic-config" icon={Settings} label="Configuração da Clínica" />
            </nav>
        </aside>

        {/* 3. MAIN CONTENT */}
        <main className="flex-1 overflow-y-auto bg-[#f2f8f9] relative flex flex-col">
            <div className="flex-1 w-full max-w-7xl mx-auto">
                {currentView === 'dashboard' && <DashboardHome />}
                {currentView === 'chat' && <ChatLayout />}
                {currentView === 'crm' && <KanbanBoard />}
                {currentView === 'followup' && <FollowUpPage />}
                {currentView === 'prompt-config' && <ConfigPromptPage />} 
                {currentView === 'clinic-config' && <IntegrationsSettings />}
                
                {/* Fallback for other mock views */}
                {['future-view'].includes(currentView) && (
                     <div className="p-8 flex flex-col items-center justify-center h-full text-center">
                        <div className="bg-white p-12 rounded-lg shadow-sm">
                            <Layers className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                            <h2 className="text-2xl font-bold text-slate-700">Page under construction</h2>
                            <p className="text-slate-500 mt-2">The requested view "{currentView}" is being built.</p>
                            <Button className="mt-6" variant="outline" onClick={() => setCurrentView('dashboard')}>Go Home</Button>
                        </div>
                     </div>
                )}
            </div>
        </main>
      </div>
    </div>
  );
}

export default App;