import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatLayout } from './components/chat/ChatLayout';
import { KanbanBoard } from './components/crm/KanbanBoard';
import { IntegrationsSettings } from './components/settings/IntegrationsSettings';
import { ConfigPromptPage } from './components/settings/ConfigPromptPage';
import { DashboardHome } from './components/dashboard/DashboardHome';
import { FollowUpPage } from './components/crm/FollowUpPage';
import { LoginPage } from './components/auth/LoginPage';
import { SignUpPage } from './components/auth/SignUpPage';
import { Button } from './components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './components/ui/avatar';
import {
    MessageSquare,
    Users,
    Settings,
    Bell,
    Home,
    Calendar as CalendarIcon,
    LayoutDashboard,
    Search,
    Plus
} from 'lucide-react';
import clsx from 'clsx';
import { fadeIn } from './utils/animations';

type ViewType = 'dashboard' | 'chat' | 'crm' | 'followup' | 'prompt-config' | 'clinic-config' | 'settings';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isSigningUp, setIsSigningUp] = useState(false);
    const [currentView, setCurrentView] = useState<ViewType>('dashboard');

    if (!isAuthenticated) {
        if (isSigningUp) {
            return <SignUpPage onBack={() => setIsSigningUp(false)} onSuccess={() => setIsSigningUp(false)} />;
        }
        return <LoginPage onLogin={() => setIsAuthenticated(true)} onSignUp={() => setIsSigningUp(true)} />;
    }

    // Jampack-Style Sidebar Item
    const SidebarItem = ({ id, icon: Icon, label, badge }: any) => {
        const isActive = currentView === id;

        return (
            <button
                onClick={() => setCurrentView(id)}
                className={clsx(
    \"w-full flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-all rounded-lg group relative\",
    isActive
        ?\"text-white bg-cyan-500 shadow-lg shadow-cyan-500/30\" 
              : \"text-slate-400 hover:text-white hover:bg-slate-700/50\"
          )
}
        >
          <Icon className={clsx(\"w-5 h-5\", isActive ? \"text-white\" : \"text-slate-400 group-hover:text-white\")} />
          <span className=\"flex-1 text-left\">{label}</span>
          {badge && (
              <span className=\"bg-cyan-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold\">
                  {badge}
              </span>
          )}
        </button>
      );
  };

  return (
    <div className=\"h-screen w-screen flex overflow-hidden bg-slate-100 font-sans\">
      
      {/* JAMPACK-STYLE DARK SIDEBAR */}
      <aside className=\"w-64 bg-slate-800 flex flex-col shadow-2xl z-30\">
          {/* Logo Header */}
          <div className=\"h-16 flex items-center gap-2 px-4 border-b border-slate-700\">
              <div className=\"w-8 h-8 bg-gradient-to-br from-cyan-500 to-teal-500 rounded-lg flex items-center justify-center text-white text-lg shadow-lg\">
                  🦷
              </div>
              <span className=\"font-bold text-white text-lg tracking-tight\">Bem-Querer</span>
          </div >

    {/* Search Bar */ }
    < div className =\"p-4\">
        < div className =\"relative\">
            < Search className =\"absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400\" />
                < input
type =\"text\" 
placeholder =\"Buscar...\" 
className =\"w-full bg-slate-700/50 text-white placeholder-slate-400 pl-10 pr-4 py-2 rounded-lg text-sm border border-slate-600 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all\"
    />
              </div >
          </div >

    {/* Navigation */ }
    < nav className =\"flex-1 overflow-y-auto px-3 pb-4 space-y-1\">
        < p className =\"text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2 mt-2\">Menu Principal</p>
            < SidebarItem id =\"dashboard\" icon={LayoutDashboard} label=\"Dashboard\" />
                < SidebarItem id =\"crm\" icon={Users} label=\"CRM\" />
                    < SidebarItem id =\"chat\" icon={MessageSquare} label=\"Chat\" badge=\"80\" />
                        < SidebarItem id =\"followup\" icon={CalendarIcon} label=\"Follow-up\" />

                            < p className =\"text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2 mt-6\">Configurações</p>
                                < SidebarItem id =\"prompt-config\" icon={Settings} label=\"Configurar Prompt\" />
                                    < SidebarItem id =\"clinic-config\" icon={Settings} label=\"Clínica\" />
          </nav >

    {/* User Profile (Bottom) */ }
    < div className =\"p-4 border-t border-slate-700\">
        < div className =\"flex items-center gap-3 cursor-pointer hover:bg-slate-700/50 p-2 rounded-lg transition-all\">
            < Avatar className =\"w-9 h-9 border-2 border-slate-600\">
                < AvatarImage src =\"https://ui-avatars.com/api/?name=Ana+Silva&background=00ACC1&color=fff\" />
                    < AvatarFallback > AS</AvatarFallback >
                  </Avatar >
    <div className=\"flex-1 min-w-0\">
        < p className =\"text-sm font-medium text-white truncate\">Dra. Ana Silva</p>
            < div className = "flex-1 min-w-0" >
        <p className="text-sm font-medium text-white truncate">Dra. Ana Silva</p>
            <p className="text-xs text-slate-400 truncate">Dentista Admin</p>
                  </div >
              </div >
          </div >
      </aside >

    {/* MAIN CONTENT AREA */ }
    < div className = "flex-1 flex flex-col overflow-hidden" >

        {/* TOP HEADER BAR (Simple, Clean) */ }
        < header className = "h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-20" >
              <div className="flex items-center gap-4">
                  <h1 className="text-xl font-semibold text-slate-800">
                      {currentView === 'dashboard' && 'Dashboard'}
                      {currentView === 'chat' && 'Chat'}
                      {currentView === 'crm' && 'CRM'}
                      {currentView === 'followup' && 'Follow-up'}
                      {currentView === 'prompt-config' && 'Configurar Prompt'}
                      {currentView === 'clinic-config' && 'Configurações da Clínica'}
                  </h1>
              </div>
              
              <div className="flex items-center gap-4">
                  <Button size="sm" className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-500/30">
                      <Plus className="w-4 h-4 mr-2" /> Novo
                  </Button>
                  
                  <div className="relative cursor-pointer hover:bg-slate-100 p-2 rounded-lg transition-all">
                      <Bell className="w-5 h-5 text-slate-600" />
                      <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                  </div>
              </div>
          </header >

    {/* CONTENT */ }
    < main className = "flex-1 overflow-y-auto bg-slate-50" >
        <AnimatePresence mode="wait">
            <motion.div
                key={currentView}
                {...fadeIn}
                className="w-full h-full"
            >
                {currentView === 'dashboard' && <DashboardHome />}
                {currentView === 'chat' && <ChatLayout />}
                {currentView === 'crm' && <KanbanBoard />}
                {currentView === 'followup' && <FollowUpPage />}
                {currentView === 'prompt-config' && <ConfigPromptPage />}
                {currentView === 'clinic-config' && <IntegrationsSettings />}
            </motion.div>
        </AnimatePresence>
          </main >
      </div >
    </div >
  );
}

export default App;