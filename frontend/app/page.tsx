"use client"

import { useState } from "react"
import { VideoStream } from "@/components/video-stream"
import { DogStatus } from "@/components/dog-status"
import { RobotControls } from "@/components/robot-controls"
import { ActivityHistory } from "@/components/activity-history"
import { SideNav } from "@/components/side-nav"

export default function Home() {
  const [activeTab, setActiveTab] = useState<"home" | "robot" | "history" | "settings">("home")

  return (
    <main className="flex min-h-screen bg-background">
      <SideNav activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Always shows video */}
        <div className="flex flex-1 flex-col overflow-auto p-4 md:p-6 lg:p-8">
          <VideoStream />
        </div>

        {/* Right Panel - Shows active tab content */}
        <div className="w-full overflow-auto border-l border-border bg-card/30 lg:w-[480px]">
          {activeTab === "home" && (
            <div className="p-4 md:p-6 lg:p-8">
              <div className="mb-6">
                <h2 className="text-balance text-3xl font-semibold text-foreground">Overview</h2>
                <p className="text-pretty text-sm text-muted-foreground">Monitor your dog's activity and wellbeing</p>
              </div>

              <div className="space-y-6">
                <DogStatus />

                <div className="rounded-3xl bg-card p-6 shadow-sm">
                  <h3 className="mb-4 text-lg font-semibold text-card-foreground">Today's Summary</h3>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="rounded-2xl bg-secondary/30 p-4">
                      <p className="text-xs font-medium text-muted-foreground">Active Time</p>
                      <p className="mt-1 text-2xl font-semibold text-card-foreground">3.5 hrs</p>
                      <p className="mt-1 text-xs text-muted-foreground">+20% from yesterday</p>
                    </div>
                    <div className="rounded-2xl bg-secondary/30 p-4">
                      <p className="text-xs font-medium text-muted-foreground">Treats Given</p>
                      <p className="mt-1 text-2xl font-semibold text-card-foreground">4</p>
                      <p className="mt-1 text-xs text-muted-foreground">2 remaining today</p>
                    </div>
                    <div className="rounded-2xl bg-secondary/30 p-4">
                      <p className="text-xs font-medium text-muted-foreground">Water Level</p>
                      <p className="mt-1 text-2xl font-semibold text-card-foreground">75%</p>
                      <p className="mt-1 text-xs text-muted-foreground">Refilled 4h ago</p>
                    </div>
                    <div className="rounded-2xl bg-secondary/30 p-4">
                      <p className="text-xs font-medium text-muted-foreground">Sleep Quality</p>
                      <p className="mt-1 text-2xl font-semibold text-card-foreground">Good</p>
                      <p className="mt-1 text-xs text-muted-foreground">8.2 hrs last night</p>
                    </div>
                  </div>
                </div>

                <div className="rounded-3xl bg-card p-6 shadow-sm">
                  <h3 className="mb-4 text-lg font-semibold text-card-foreground">Recent Activity</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3 rounded-2xl bg-secondary/30 p-3">
                      <div className="mt-0.5 h-2 w-2 rounded-full bg-accent" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-card-foreground">Playing with ball</p>
                        <p className="text-xs text-muted-foreground">5 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 rounded-2xl bg-secondary/30 p-3">
                      <div className="mt-0.5 h-2 w-2 rounded-full bg-primary" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-card-foreground">Snack time</p>
                        <p className="text-xs text-muted-foreground">32 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 rounded-2xl bg-secondary/30 p-3">
                      <div className="mt-0.5 h-2 w-2 rounded-full bg-chart-4" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-card-foreground">Nap time</p>
                        <p className="text-xs text-muted-foreground">1 hour ago</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "robot" && (
            <div className="p-4 md:p-6 lg:p-8">
              <RobotControls />
            </div>
          )}

          {activeTab === "history" && (
            <div className="p-4 md:p-6 lg:p-8">
              <ActivityHistory />
            </div>
          )}

          {activeTab === "settings" && (
            <div className="p-4 md:p-6 lg:p-8">
              <div className="mb-6">
                <h2 className="text-balance text-3xl font-semibold text-foreground">Settings</h2>
                <p className="text-pretty text-sm text-muted-foreground">Configure your preferences</p>
              </div>
              <div className="space-y-4">
                <div className="rounded-2xl bg-card p-6 shadow-sm">
                  <h3 className="mb-2 text-base font-medium text-card-foreground">Camera Settings</h3>
                  <p className="text-sm text-muted-foreground">Configure video quality and recording</p>
                </div>
                <div className="rounded-2xl bg-card p-6 shadow-sm">
                  <h3 className="mb-2 text-base font-medium text-card-foreground">Robot Arm Settings</h3>
                  <p className="text-sm text-muted-foreground">Adjust robot arm sensitivity</p>
                </div>
                <div className="rounded-2xl bg-card p-6 shadow-sm">
                  <h3 className="mb-2 text-base font-medium text-card-foreground">Notifications</h3>
                  <p className="text-sm text-muted-foreground">Manage alerts and preferences</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
