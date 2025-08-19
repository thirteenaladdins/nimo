import { svelte } from "@sveltejs/vite-plugin-svelte"

export default {
  plugins: [svelte()],
  build: {
    target: 'esnext',
    rollupOptions: {
      external: []
    }
  }
}
