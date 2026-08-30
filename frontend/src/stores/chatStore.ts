import { create } from 'zustand'

export interface Message { role: 'user' | 'assistant'; content: string; evidence?: any[]; risk?: any }

interface ChatState {
  messages: Message[]
  loading: boolean
  addMessage: (m: Message) => void
  setLoading: (v: boolean) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  setLoading: (v) => set({ loading: v }),
}))
