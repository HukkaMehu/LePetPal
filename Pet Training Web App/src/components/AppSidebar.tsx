import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
} from './ui/sidebar';
import { Video, Images, BarChart3, ListChecks, Settings } from 'lucide-react';
import { Separator } from './ui/separator';

interface AppSidebarProps {
  currentPage: 'live' | 'gallery' | 'analytics' | 'routines' | 'settings';
  onNavigate: (page: 'live' | 'gallery' | 'analytics' | 'routines' | 'settings') => void;
}

export function AppSidebar({ currentPage, onNavigate }: AppSidebarProps) {
  const menuItems = [
    { id: 'live' as const, icon: Video, label: 'Live' },
    { id: 'gallery' as const, icon: Images, label: 'Gallery' },
    { id: 'analytics' as const, icon: BarChart3, label: 'Analytics' },
    { id: 'routines' as const, icon: ListChecks, label: 'Routines' },
  ];

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-border p-4">
        <h2 className="text-foreground">PetLink</h2>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {menuItems.map((item) => (
            <SidebarMenuItem key={item.id}>
              <SidebarMenuButton
                isActive={currentPage === item.id}
                onClick={() => onNavigate(item.id)}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
        <Separator className="my-2" />
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              isActive={currentPage === 'settings'}
              onClick={() => onNavigate('settings')}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="border-t border-border p-4">
        <p className="text-xs text-muted-foreground">Version 1.0.0</p>
      </SidebarFooter>
    </Sidebar>
  );
}
