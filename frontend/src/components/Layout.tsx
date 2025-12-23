import { ReactNode } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import {
  LayoutDashboard,
  Ticket,
  Wrench,
  Calendar,
  Users,
  UserCog,
  Settings,
  LogOut,
  Menu,
} from 'lucide-react';
import Button from './ui/Button';

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Ticket', href: '/tickets', icon: Ticket },
  { name: 'Interventi', href: '/interventions', icon: Wrench },
  { name: 'Calendario', href: '/calendar', icon: Calendar },
  { name: 'Clienti', href: '/clients', icon: Users },
  { name: 'Tecnici', href: '/technicians', icon: UserCog },
];

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border">
        {/* Logo */}
        <div className="flex h-16 items-center px-6 border-b border-border">
          <h1 className="text-2xl font-bold text-primary">DAAssist</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
                {user?.nome?.[0]}{user?.cognome?.[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user?.nome} {user?.cognome}
                </p>
                <p className="text-xs text-muted-foreground truncate">{user?.ruolo}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-background px-6">
          <div className="flex-1">
            <h2 className="text-lg font-semibold">
              {navigation.find((item) => item.href === location.pathname)?.name || 'DAAssist'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            {/* Placeholder per notifiche, ricerca, etc. */}
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
