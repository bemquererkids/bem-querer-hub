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
import { Navbar } from './components/layout/Navbar';

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
                <Navbar />

                {/* SCROLLABLE VIEWPORT */}
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