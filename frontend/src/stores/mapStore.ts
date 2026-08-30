import { create } from 'zustand'

interface MapState {
  center: [number, number]
  pfz: any[]
  selectedPfz: any | null
  layers: { pfz: boolean; mpa: boolean; eez: boolean }
  setCenter: (c: [number, number]) => void
  setPfz: (p: any[]) => void
  setSelected: (p: any) => void
  toggleLayer: (k: 'pfz' | 'mpa' | 'eez') => void
}

export const useMapStore = create<MapState>((set) => ({
  center: [72.8, 19.0],
  pfz: [],
  selectedPfz: null,
  layers: { pfz: true, mpa: true, eez: true },
  setCenter: (c) => set({ center: c }),
  setPfz: (p) => set({ pfz: p }),
  setSelected: (p) => set({ selectedPfz: p }),
  toggleLayer: (k) => set((s) => ({ layers: { ...s.layers, [k]: !s.layers[k] } })),
}))
