import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(async ({ mode }) => {
	const isDev = mode === 'development'
	const frappeui = await importFrappeUIPlugin(isDev)

	const config = {
		define: {
			__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
		},
		plugins: [
			{
				name: 'virtual-common-site-config',
				resolveId(id) {
					if (id.endsWith('common_site_config.json')) {
						const resolvedPath = path.resolve(__dirname, id)
						if (!fs.existsSync(resolvedPath)) {
							return '\0virtual:common_site_config.json'
						}
					}
					return null
				},
				load(id) {
					if (id === '\0virtual:common_site_config.json') {
						return JSON.stringify({ socketio_port: 9000 })
					}
					return null
				},
			},
			frappeui({
				frappeProxy: true,
				lucideIcons: true,
				jinjaBootData: true,
				buildConfig: {
					indexHtmlPath: '../lms/www/_lms.html',
				},
			}),
			vue(),
			VitePWA({
				registerType: 'autoUpdate',
				injectRegister: false,
				devOptions: {
					enabled: false,
				},
				workbox: {
					cleanupOutdatedCaches: true,
					inlineWorkboxRuntime: true,
					maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
					globPatterns: ['**/*.{js,ts,css,svg}'],
					modifyURLPrefix: {
						'': '/assets/lms/frontend/',
					},
					navigateFallback: null,
					runtimeCaching: [
						{
							urlPattern: ({ request }) =>
								request.destination === 'document',
							handler: 'NetworkFirst',
							options: {
								cacheName: 'html-cache',
							},
						},
					],
				},
				manifest: false,
			}),
		],
		server: {
			host: '0.0.0.0', // Accept connections from any network interface
			allowedHosts: true,
		},
		resolve: {
			alias: {
				'@': path.resolve(__dirname, 'src'),
			},
		},
		optimizeDeps: {
			include: [
				'feather-icons',
				'tailwind.config.js',
				'interactjs',
				'highlight.js',
				'plyr',
			],
			exclude: mode === 'production' ? [] : ['frappe-ui'],
		},
	}
	return config
})

async function importFrappeUIPlugin(isDev) {
	if (isDev) {
		try {
			const module = await import('../frappe-ui/vite')
			return module.default
		} catch (error) {
			console.warn(
				'Local frappe-ui not found, falling back to npm package:',
				error.message
			)
		}
	}
	// Fall back to npm package if local import fails
	const module = await import('frappe-ui/vite')
	return module.default
}
