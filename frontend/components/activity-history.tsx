"use client"

import { Cookie, CircleDot, Camera, Hand } from "lucide-react"

const activities = [
  { id: 1, type: "snack", message: "Snack given", time: "12:03 PM", icon: Cookie },
  { id: 2, type: "camera", message: "Dog seen at camera", time: "11:45 AM", icon: Camera },
  { id: 3, type: "play", message: "Played with ball", time: "10:20 AM", icon: CircleDot },
  { id: 4, type: "pet", message: "Pet interaction", time: "9:15 AM", icon: Hand },
  { id: 5, type: "snack", message: "Snack given", time: "8:30 AM", icon: Cookie },
  { id: 6, type: "camera", message: "Dog seen at camera", time: "7:45 AM", icon: Camera },
]

export function ActivityHistory() {
  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <h1 className="mb-2 text-3xl font-semibold text-foreground">Activity History</h1>
        <p className="text-muted-foreground">Recent interactions with your dog</p>
      </div>

      <div className="rounded-3xl bg-card p-6 shadow-sm">
        <div className="space-y-4">
          {activities.map((activity, index) => {
            const Icon = activity.icon
            return (
              <div
                key={activity.id}
                className={`flex items-start gap-4 ${
                  index !== activities.length - 1 ? "border-b border-border pb-4" : ""
                }`}
              >
                <div className="rounded-full bg-secondary p-3">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-card-foreground">{activity.message}</p>
                  <p className="text-sm text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
