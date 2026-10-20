import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Allow requests from any host during development/testing
    // This is the easiest fix for Ngrok/Cloudflare tunnels
    allowedHosts: true, 
    
    // OR, if you want to be stricter, specify the exact Ngrok URL:
    // allowedHosts: ['prowling-frayed-fax.ngrok-free.dev'],
    
    host: true, // Optional: Ensures Vite listens on all network interfaces
  },
})