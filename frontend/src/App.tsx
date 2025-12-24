import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatLayout } from './components/chat/ChatLayout';
import { KanbanBoard } from './components/crm/KanbanBoard';
import { IntegrationsSettings } from './components/settings/IntegrationsSettings';
import { ConfigPromptPage } from './components/settings/ConfigPromptPage';
import { InviteManagementPage } from './components/settings/InviteManagementPage';
import { ModulesSettingsPage } from './components/settings/ModulesSettingsPage';
import { DashboardHome } from './components/dashboard/DashboardHome';
import { FollowUpPage } from './components/crm/FollowUpPage';
import { LoginPage } from './components/auth/LoginPage';
import { SignUpPage } from './components/auth/SignUpPage';
import { fadeIn } from './utils/animations';
import { Sidebar, ViewType } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { AuthProvider, useAuth } from './context/AuthContext';

function AppContent() {
    const { isAuthenticated, login } = useAuth();
    const [isSigningUp, setIsSigningUp] = useState(false);
    const [currentView, setCurrentView] = useState<ViewType>('dashboard');
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    if (!isAuthenticated) {
        if (isSigningUp) {
            return <SignUpPage onBack={() => setIsSigningUp(false)} onSuccess={() => setIsSigningUp(false)} />;
        }
        // Pass the handleLogin wrapper to match expected signature
        return <LoginPage onLogin={() => { }} onSignUp={() => setIsSigningUp(true)} />;
    }

    return (
        <div className="h-screen w-screen flex overflow-hidden bg-background font-sans transition-colors duration-300 relative selection:bg-cyan-500/30">
            {/* Grid Pattern Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute inset-0 bg-[repeating-linear-gradient(315deg,var(--grid-line-color)_0,var(--grid-line-color)_1px,transparent_0,transparent_50%)] bg-[length:10px_10px] opacity-20"></div>
            </div>

            <Sidebar
                currentView={currentView}
                setCurrentView={setCurrentView}
                isMobileMenuOpen={isMobileMenuOpen}
                setIsMobileMenuOpen={setIsMobileMenuOpen}
            />

            {/* MAIN CONTENT AREA */}
            <div className="flex-1 flex flex-col overflow-hidden z-10">
                <Navbar onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />

                {/* SCROLLABLE VIEWPORT */}
                <main className="flex-1 overflow-y-auto bg-background transition-colors duration-300">
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
                            {currentView === 'modules-settings' && <ModulesSettingsPage />}
                            {currentView === 'invite-management' && <InviteManagementPage />}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>
        </div>
    );
}

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;