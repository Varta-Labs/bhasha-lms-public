let pdfJsPromise

const loadPdfJs = async () => {
	if (!pdfJsPromise) {
		pdfJsPromise = Promise.all([
			import('pdfjs-dist'),
			import('pdfjs-dist/build/pdf.worker.min.mjs?url'),
		]).then(([pdfjs, worker]) => {
			pdfjs.GlobalWorkerOptions.workerSrc = worker.default
			return pdfjs
		})
	}
	return pdfJsPromise
}

const makeButton = (label, symbol, onClick) => {
	const button = document.createElement('button')
	button.type = 'button'
	button.className = 'bhasha-slide-deck__button'
	button.setAttribute('aria-label', label)
	button.title = label
	button.textContent = symbol
	button.addEventListener('click', onClick)
	return button
}

export default class SlideDeck {
	static get isReadOnlySupported() {
		return true
	}

	constructor({ data }) {
		this.data = data || {}
		this.pageNumber = 1
		this.renderToken = 0
		this.fullscreenFallback = false
	}

	render() {
		this.root = document.createElement('section')
		this.root.className = 'bhasha-slide-deck'
		this.root.setAttribute('aria-label', 'Lesson presentation')

		this.stage = document.createElement('div')
		this.stage.className = 'bhasha-slide-deck__stage is-loading'
		this.status = document.createElement('span')
		this.status.className = 'bhasha-slide-deck__status'
		this.status.setAttribute('aria-live', 'polite')
		this.status.textContent = 'Loading presentation…'
		this.stage.append(this.status)

		this.canvas = document.createElement('canvas')
		this.canvas.className = 'bhasha-slide-deck__canvas'

		this.previousButton = makeButton('Previous slide', '←', () =>
			this.changePage(-1),
		)
		this.fullscreenButton = makeButton('Enter full screen', '⛶', () =>
			this.toggleFullscreen(),
		)
		this.nextButton = makeButton('Next slide', '→', () =>
			this.changePage(1),
		)
		this.pageStatus = document.createElement('span')
		this.pageStatus.className = 'bhasha-slide-deck__page-status'
		this.pageStatus.setAttribute('aria-live', 'polite')

		const controls = document.createElement('div')
		controls.className = 'bhasha-slide-deck__controls'
		controls.append(
			this.previousButton,
			this.pageStatus,
			this.fullscreenButton,
			this.nextButton,
		)
		this.root.append(this.stage, controls)

		this.resizeObserver = new ResizeObserver(() => {
			if (!this.pdf || !this.stage.clientWidth) return
			window.clearTimeout(this.resizeTimer)
			this.resizeTimer = window.setTimeout(() => this.renderPage(), 100)
		})
		this.resizeObserver.observe(this.stage)
		this.handleFullscreenChange = () => this.updateFullscreenState()
		this.handleKeydown = (event) => this.onKeydown(event)
		document.addEventListener('fullscreenchange', this.handleFullscreenChange)
		document.addEventListener('keydown', this.handleKeydown)
		this.load()

		return this.root
	}

	async load() {
		try {
			const pdfjs = await loadPdfJs()
			const deckUrl = new URL(this.data.url, window.location.origin)
			this.loadingTask = pdfjs.getDocument({
				url: deckUrl.href,
				withCredentials: deckUrl.origin === window.location.origin,
			})
			this.pdf = await this.loadingTask.promise
			this.stage.classList.remove('is-loading')
			this.stage.replaceChildren(this.canvas)
			await this.renderPage()
		} catch (error) {
			console.error('Presentation failed to load:', error?.message, error)
			this.stage.classList.remove('is-loading')
			this.status.textContent = 'Presentation unavailable. Please try again.'
			this.stage.replaceChildren(this.status)
		}
	}

	async renderPage() {
		if (!this.pdf || !this.stage.clientWidth) return
		const token = ++this.renderToken
		this.renderTask?.cancel()
		const page = await this.pdf.getPage(this.pageNumber)
		const initialViewport = page.getViewport({ scale: 1 })
		const widthScale = this.stage.clientWidth / initialViewport.width
		const isFullscreen =
			document.fullscreenElement === this.root || this.fullscreenFallback
		const heightScale = isFullscreen
			? this.stage.clientHeight / initialViewport.height
			: widthScale
		const cssScale = Math.min(widthScale, heightScale)
		const cssWidth = initialViewport.width * cssScale
		const pixelRatio = Math.min(window.devicePixelRatio || 1, 2)
		const viewport = page.getViewport({ scale: cssScale * pixelRatio })
		if (token !== this.renderToken) return

		this.canvas.width = Math.floor(viewport.width)
		this.canvas.height = Math.floor(viewport.height)
		this.canvas.style.width = `${cssWidth}px`
		this.canvas.style.height = `${initialViewport.height * cssScale}px`
		this.renderTask = page.render({
			canvasContext: this.canvas.getContext('2d'),
			viewport,
		})
		try {
			await this.renderTask.promise
		} catch (error) {
			if (error?.name === 'RenderingCancelledException') return
			throw error
		}
		this.updateControls()
	}

	changePage(offset) {
		const nextPage = this.pageNumber + offset
		if (!this.pdf || nextPage < 1 || nextPage > this.pdf.numPages) return
		this.pageNumber = nextPage
		this.renderPage()
	}

	updateControls() {
		this.previousButton.disabled = this.pageNumber <= 1
		this.nextButton.disabled = this.pageNumber >= this.pdf.numPages
		this.pageStatus.textContent = `${this.pageNumber} / ${this.pdf.numPages}`
	}

	async toggleFullscreen() {
		if (document.fullscreenElement === this.root) {
			await document.exitFullscreen()
			return
		}
		if (this.fullscreenFallback) {
			this.exitFullscreenFallback()
			return
		}
		const requestFullscreen =
			this.root.requestFullscreen || this.root.webkitRequestFullscreen
		if (requestFullscreen) {
			try {
				await requestFullscreen.call(this.root)
				return
			} catch (error) {
				console.warn('Native full screen was unavailable.', error)
			}
		}
		this.fullscreenFallback = true
		this.root.classList.add('is-fullscreen-fallback')
		document.body.classList.add('bhasha-slide-deck-open')
		this.updateFullscreenState()
	}

	updateFullscreenState() {
		const isFullscreen =
			document.fullscreenElement === this.root || this.fullscreenFallback
		this.fullscreenButton.setAttribute(
			'aria-label',
			isFullscreen ? 'Exit full screen' : 'Enter full screen',
		)
		this.fullscreenButton.title = isFullscreen
			? 'Exit full screen'
			: 'Enter full screen'
		this.renderPage()
	}

	exitFullscreenFallback() {
		this.fullscreenFallback = false
		this.root.classList.remove('is-fullscreen-fallback')
		document.body.classList.remove('bhasha-slide-deck-open')
		this.updateFullscreenState()
	}

	onKeydown(event) {
		const isFullscreen =
			document.fullscreenElement === this.root || this.fullscreenFallback
		if (!isFullscreen) return
		if (event.key === 'ArrowLeft') this.changePage(-1)
		if (event.key === 'ArrowRight') this.changePage(1)
		if (event.key === 'Escape' && this.fullscreenFallback) {
			this.exitFullscreenFallback()
		}
	}

	save() {
		return this.data
	}

	destroy() {
		this.renderToken += 1
		this.renderTask?.cancel()
		window.clearTimeout(this.resizeTimer)
		this.resizeObserver?.disconnect()
		document.removeEventListener('fullscreenchange', this.handleFullscreenChange)
		document.removeEventListener('keydown', this.handleKeydown)
		if (this.fullscreenFallback) this.exitFullscreenFallback()
		this.loadingTask?.destroy()
		this.pdf?.destroy()
	}
}
