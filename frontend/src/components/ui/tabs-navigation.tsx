import React from 'react';
import { LucideIcon } from 'lucide-react';
import clsx from 'clsx';

export interface TabItem {
    id: string;
    label: string;
    icon: LucideIcon;
}

interface TabsNavigationProps {
    tabs: TabItem[];
    activeTab: string;
    onChange: (tabId: string) => void;
}

export const TabsNavigation: React.FC<TabsNavigationProps> = ({ tabs, activeTab, onChange }) => {
    return (
        <div className="border-b border-gray-200 mb-6">
            {/* Mobile Dropdown Fallback */}
            <div className="sm:hidden mb-4">
                <label htmlFor="tabs" className="sr-only">
                    Selecionar aba
                </label>
                <select
                    id="tabs"
                    name="tabs"
                    className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-cyan-500 focus:outline-none focus:ring-cyan-500 sm:text-sm"
                    value={activeTab}
                    onChange={(e) => onChange(e.target.value)}
                >
                    {tabs.map((tab) => (
                        <option key={tab.id} value={tab.id}>
                            {tab.label}
                        </option>
                    ))}
                </select>
            </div>

            {/* Desktop View */}
            <div className="hidden sm:block">
                <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;

                        return (
                            <button
                                key={tab.id}
                                onClick={() => onChange(tab.id)}
                                className={clsx(
                                    "group inline-flex items-center border-b-2 py-4 px-1 text-sm font-medium transition-all",
                                    isActive
                                        ? "border-cyan-500 text-cyan-600 font-bold"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                                )}
                                aria-current={isActive ? 'page' : undefined}
                            >
                                <Icon
                                    className={clsx(
                                        "-ml-0.5 mr-2 h-5 w-5 transition-colors",
                                        isActive ? "text-cyan-500" : "text-gray-400 group-hover:text-gray-500"
                                    )}
                                    aria-hidden="true"
                                />
                                <span>{tab.label}</span>
                            </button>
                        );
                    })}
                </nav>
            </div>
        </div>
    );
};
