import React from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Checkbox } from '../ui/checkbox';
import { Slider } from '../ui/slider';
import { Progress } from '../ui/progress';

import { 
    Bell, 
    Check, 
    ChevronRight, 
    Terminal, 
    Loader2, 
    Mail, 
    Settings, 
    User, 
    CreditCard, 
    Keyboard, 
    Users, 
    Plus,
    Calendar as CalendarIcon,
    Cloud
} from 'lucide-react';

export const UIElementsPage: React.FC = () => {
    return (
        <div className="p-8 space-y-8 animate-in fade-in duration-500 pb-20">
            
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight text-slate-800">UI Components</h1>
                <p className="text-muted-foreground">
                    A comprehensive suite of Shadcn UI components fully styled for the Bem-Querer design system.
                </p>
            </div>

            {/* 1. BUTTONS & BADGES */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Buttons</CardTitle>
                        <CardDescription>Primary, secondary, outline, and ghost variants.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-wrap gap-4">
                        <Button>Default</Button>
                        <Button variant="secondary">Secondary</Button>
                        <Button variant="destructive">Destructive</Button>
                        <Button variant="outline">Outline</Button>
                        <Button variant="ghost">Ghost</Button>
                        <Button variant="link">Link</Button>
                        <Button disabled>Disabled</Button>
                        <Button size="icon"><Mail className="w-4 h-4" /></Button>
                        <Button className="gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Please wait</Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Badges</CardTitle>
                        <CardDescription>Status indicators and labels.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-wrap gap-4">
                        <Badge>Default</Badge>
                        <Badge variant="secondary">Secondary</Badge>
                        <Badge variant="destructive">Destructive</Badge>
                        <Badge variant="outline">Outline</Badge>
                        <Badge className="bg-emerald-500 hover:bg-emerald-600">Success</Badge>
                        <Badge className="bg-amber-500 hover:bg-amber-600">Warning</Badge>
                    </CardContent>
                </Card>
            </div>

            {/* 2. FORM CONTROLS */}
            <Card>
                <CardHeader>
                    <CardTitle>Form Elements</CardTitle>
                    <CardDescription>Inputs, switches, checkboxes and sliders.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <div className="grid w-full max-w-sm items-center gap-1.5">
                                <Label htmlFor="email">Email</Label>
                                <Input type="email" id="email" placeholder="Email" />
                            </div>
                            <div className="grid w-full max-w-sm items-center gap-1.5">
                                <Label htmlFor="file">Picture</Label>
                                <Input id="file" type="file" />
                            </div>
                        </div>
                        
                        <div className="space-y-4">
                            <div className="flex items-center space-x-2">
                                <Switch id="airplane-mode" />
                                <Label htmlFor="airplane-mode">Airplane Mode</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox id="terms" />
                                <Label htmlFor="terms">Accept terms and conditions</Label>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4 pt-4 border-t">
                        <Label>Volume (Slider)</Label>
                        <Slider defaultValue={[50]} max={100} step={1} className="w-[60%]" />
                    </div>
                </CardContent>
            </Card>

            {/* 3. TABS & CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="h-full">
                    <CardHeader>
                        <CardTitle>Tabs & Navigation</CardTitle>
                        <CardDescription>Organize content into separate views.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Tabs defaultValue="account" className="w-full">
                            <TabsList className="grid w-full grid-cols-2">
                                <TabsTrigger value="account">Account</TabsTrigger>
                                <TabsTrigger value="password">Password</TabsTrigger>
                            </TabsList>
                            <TabsContent value="account">
                                <div className="space-y-4 py-4">
                                    <div className="space-y-1">
                                        <Label>Name</Label>
                                        <Input defaultValue="Pedro Duarte" />
                                    </div>
                                    <div className="space-y-1">
                                        <Label>Username</Label>
                                        <Input defaultValue="@pedro" />
                                    </div>
                                    <Button>Save changes</Button>
                                </div>
                            </TabsContent>
                            <TabsContent value="password">
                                <div className="space-y-4 py-4">
                                    <div className="space-y-1">
                                        <Label>Current Password</Label>
                                        <Input type="password" />
                                    </div>
                                    <div className="space-y-1">
                                        <Label>New Password</Label>
                                        <Input type="password" />
                                    </div>
                                    <Button>Change password</Button>
                                </div>
                            </TabsContent>
                        </Tabs>
                    </CardContent>
                </Card>

                {/* 4. ALERTS & FEEDBACK */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Alerts</CardTitle>
                            <CardDescription>Callout messages for user attention.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Alert>
                                <Terminal className="h-4 w-4" />
                                <AlertTitle>Heads up!</AlertTitle>
                                <AlertDescription>
                                    You can add components to your app using the cli.
                                </AlertDescription>
                            </Alert>
                            <Alert variant="destructive">
                                <Terminal className="h-4 w-4" />
                                <AlertTitle>Error</AlertTitle>
                                <AlertDescription>
                                    Your session has expired. Please log in again.
                                </AlertDescription>
                            </Alert>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Progress</CardTitle>
                            <CardDescription>Display progress status.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs">
                                    <span>Downloading...</span>
                                    <span>33%</span>
                                </div>
                                <Progress value={33} />
                            </div>
                             <div className="space-y-2">
                                <div className="flex justify-between text-xs">
                                    <span>Setup</span>
                                    <span>88%</span>
                                </div>
                                <Progress value={88} className="[&>div]:bg-green-500" />
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* 5. SKELETON & STATES (Mock) */}
             <Card>
                <CardHeader>
                    <CardTitle>Loading States</CardTitle>
                    <CardDescription>Skeleton screens for loading content.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center space-x-4">
                        <div className="h-12 w-12 rounded-full bg-slate-200 animate-pulse" />
                        <div className="space-y-2">
                            <div className="h-4 w-[250px] bg-slate-200 animate-pulse rounded" />
                            <div className="h-4 w-[200px] bg-slate-200 animate-pulse rounded" />
                        </div>
                    </div>
                </CardContent>
            </Card>

        </div>
    );
};