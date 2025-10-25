"use client"

import { Home, Bot, Clock, Settings } from "lucide-react"

interface SideNavProps {
  activeTab: "home" | "robot" | "history" | "settings"
  onTabChange: (tab: "home" | "robot" | "history" | "settings") => void
}

export function SideNav({ activeTab, onTabChange }: SideNavProps) {
  const tabs = [
    { id: "home" as const, label: "Home", icon: Home },
    { id: "robot" as const, label: "Robot", icon: Bot },
    { id: "history" as const, label: "History", icon: Clock },
    { id: "settings" as const, label: "Settings", icon: Settings },
  ]

  return (
    <nav className="flex h-screen w-20 flex-col items-center border-r border-border bg-sidebar py-6 md:w-24">
      <div className="mb-8 flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground md:h-12 md:w-12">
        <Bot className="h-6 w-6 md:h-7 md:w-7" />
      </div>

      <div className="flex flex-1 flex-col gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center gap-1.5 rounded-xl px-3 py-3 transition-all ${
                isActive
                  ? "bg-sidebar-accent text-sidebar-primary"
                  : "text-sidebar-foreground/60 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
              }`}
              title={tab.label}
            >
              <Icon className={`h-6 w-6 ${isActive ? "fill-sidebar-primary/10" : ""}`} />
              <span className="text-[10px] font-medium md:text-xs">{tab.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
