import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		host: '0.0.0.0',           // allow LAN/NGINX access
		port: 5173,                 // Vite listens here
		strictPort: true,
		allowedHosts: ['kuberaudit.ddns.net'],
		hmr: {
			protocol: 'wss',          // browser connects via WSS
			host: 'kuberaudit.ddns.net',
			port: 5173                // **Vite dev server port**, not 443
		},
		proxy: {
			'/api': 'http://127.0.0.1:8000'
		}
	}
});
