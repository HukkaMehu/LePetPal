"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Cookie, CircleDot, Hand, Waves } from "lucide-react"

export function RobotControls() {
  const [isManualMode, setIsManualMode] = useState(false)

  const handleAction = (action: string) => {
    console.log(`Robot action: ${action}`)
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="mb-2 text-2xl font-semibold text-foreground">Robot Control</h2>
        <p className="text-sm text-muted-foreground">Interact with your dog remotely</p>
      </div>

      <div className="space-y-4">
        {/* Quick Actions */}
        <div className="rounded-2xl bg-card p-5 shadow-sm">
          <h3 className="mb-4 text-base font-medium text-card-foreground">Quick Actions</h3>
          <div className="grid gap-3">
            <Button
              size="lg"
              className="h-16 rounded-xl bg-accent text-accent-foreground hover:bg-accent/90"
              onClick={() => handleAction("give-snack")}
            >
              <Cookie className="mr-3 h-5 w-5" />
              <span>Give Snack</span>
            </Button>

            <Button
              size="lg"
              className="h-16 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={() => handleAction("play-ball")}
            >
              <CircleDot className="mr-3 h-5 w-5" />
              <span>Play Ball</span>
            </Button>

            <Button
              size="lg"
              className="h-16 rounded-xl bg-chart-3 text-white hover:bg-chart-3/90"
              onClick={() => handleAction("pet-dog")}
            >
              <Hand className="mr-3 h-5 w-5" />
              <span>Pet Dog</span>
            </Button>

            <Button
              size="lg"
              className="h-16 rounded-xl bg-chart-4 text-white hover:bg-chart-4/90"
              onClick={() => handleAction("wave-hello")}
            >
              <Waves className="mr-3 h-5 w-5" />
              <span>Wave Hello</span>
            </Button>
          </div>
        </div>

        {/* Manual Control */}
        <div className="rounded-2xl bg-card p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-base font-medium text-card-foreground">Manual Control</h3>
            <Button
              variant={isManualMode ? "default" : "outline"}
              size="sm"
              className="rounded-full"
              onClick={() => setIsManualMode(!isManualMode)}
            >
              {isManualMode ? "Enabled" : "Disabled"}
            </Button>
          </div>

          {isManualMode ? (
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-card-foreground">Arm Position</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  className="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-primary"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-card-foreground">Rotation</label>
                <input
                  type="range"
                  min="0"
                  max="360"
                  className="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-primary"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-card-foreground">Grip Strength</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  className="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-primary"
                />
              </div>
            </div>
          ) : (
            <p className="text-center text-sm text-muted-foreground">
              Enable manual control to adjust robot arm settings
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
