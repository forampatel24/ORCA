import { create } from "zustand"
export type PrimaryCategory = "fishing" | "marine" | "safety" | "navigation" | null
export type SubViz =
  | "pfz" | "sst" | "chl" | "fish"
  | "wind" | "waves" | "currents" | "weather" | "sea"
  | "cyclone" | "lightning" | "mpa" | "restricted" | "alerts"
  | "vessel" | "ports" | "eez" | "route" | "geofence"
  | null

interface VizState {
  sidebarOpen: boolean
  activeCategory: PrimaryCategory
  activeSub: SubViz
  setSidebarOpen: (o: boolean) => void
  setActiveCategory: (c: PrimaryCategory) => void
  setActiveSub: (s: SubViz) => void
}
export const useVizStore = create<VizState>((set) => ({
  sidebarOpen: true,
  activeCategory: null,
  activeSub: null,
  setSidebarOpen: (o) => set({ sidebarOpen: o }),
  setActiveCategory: (c) => set({ activeCategory: c, activeSub: null }),
  setActiveSub: (s) => set({ activeSub: s }),
}))
