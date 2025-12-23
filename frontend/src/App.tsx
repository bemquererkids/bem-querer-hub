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
import {
    Bell,
    Plus
} from 'lucide-react';
import { fadeIn } from './utils/animations';
import { Sidebar, ViewType } from './components/layout/Sidebar';

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

    return (
        <div className="h-screen w-screen flex overflow-hidden bg-slate-100 font-sans">
            <Sidebar currentView={currentView} setCurrentView={setCurrentView} />


            {/* MAIN CONTENT AREA */}
            <div className="flex-1 flex flex-col overflow-hidden">

                {/* TOP HEADER BAR (Simple, Clean) */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-20">
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
                </header>

                {/* CONTENT */}
                <main className="flex-1 overflow-y-auto bg-slate-50">
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
                </main>
            </div>
        </div>
    );
}

export default App;