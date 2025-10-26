"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, Maximize2, Camera } from "lucide-react"

export function VideoStream() {
  const [isMuted, setIsMuted] = useState(true)
  const [status, setStatus] = useState<"online" | "offline" | "connecting">("online")

  const handleTakePhoto = () => {
    console.log("Photo taken!")
  }

  const handleFullscreen = () => {
    console.log("Fullscreen toggled")
  }

  return (
    <div className="relative w-full overflow-hidden rounded-3xl bg-card shadow-lg">
      {/* Status Badge */}
      <div className="absolute left-4 top-4 z-10">
        <div
          className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium backdrop-blur-sm ${
            status === "online"
              ? "bg-accent/90 text-accent-foreground"
              : status === "connecting"
                ? "bg-muted/90 text-muted-foreground"
                : "bg-destructive/90 text-destructive-foreground"
          }`}
        >
          <div
            className={`h-2 w-2 rounded-full ${
              status === "online"
                ? "bg-accent-foreground animate-pulse"
                : status === "connecting"
                  ? "bg-muted-foreground"
                  : "bg-destructive-foreground"
            }`}
          />
          {status === "online" ? "Online" : status === "connecting" ? "Connecting..." : "Offline"}
        </div>
      </div>

      {/* Video Feed */}
      <div className="relative aspect-video w-full bg-muted">
        <img
          src="/happy-golden-retriever-dog-playing-in-living-room.jpg"
          alt="Live video feed of your dog"
          className="h-full w-full object-cover"
        />
      </div>

      {/* Control Overlay */}
      <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 items-center gap-2">
        <Button
          size="icon"
          variant="secondary"
          className="h-12 w-12 rounded-full bg-card/90 backdrop-blur-sm hover:bg-card"
          onClick={() => setIsMuted(!isMuted)}
        >
          {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </Button>

        <Button
          size="lg"
          className="h-12 rounded-full bg-primary px-6 text-primary-foreground hover:bg-primary/90"
          onClick={handleTakePhoto}
        >
          <Camera className="mr-2 h-5 w-5" />
          Take Photo
        </Button>

        <Button
          size="icon"
          variant="secondary"
          className="h-12 w-12 rounded-full bg-card/90 backdrop-blur-sm hover:bg-card"
          onClick={handleFullscreen}
        >
          <Maximize2 className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
}
