"use client"

import { Heart, Activity, UtensilsCrossed } from "lucide-react"

export function DogStatus() {
  return (
    <div className="rounded-3xl bg-card p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-balance text-2xl font-semibold text-card-foreground">Max</h2>
        <p className="text-pretty text-sm text-muted-foreground">Golden Retriever, 3 years old</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="flex flex-1 min-w-0 items-start gap-3 rounded-2xl bg-accent/10 p-4">
          <div className="flex-shrink-0 rounded-full bg-accent/20 p-2.5">
            <Heart className="h-5 w-5 text-accent" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Mood</p>
            <p className="mt-0.5 text-lg font-semibold text-card-foreground">Happy</p>
          </div>
        </div>

        <div className="flex flex-1 min-w-0 items-start gap-3 rounded-2xl bg-primary/10 p-4">
          <div className="flex-shrink-0 rounded-full bg-primary/20 p-2.5">
            <Activity className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Activity</p>
            <p className="mt-0.5 text-lg font-semibold text-card-foreground">Playing</p>
          </div>
        </div>

        <div className="flex flex-1 min-w-0 items-start gap-3 rounded-2xl bg-chart-4/10 p-4">
          <div className="flex-shrink-0 rounded-full bg-chart-4/20 p-2.5">
            <UtensilsCrossed className="h-5 w-5 text-chart-4" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Last Fed</p>
            <p className="mt-0.5 text-lg font-semibold text-card-foreground">2h ago</p>
          </div>
        </div>
      </div>
    </div>
  )
}
