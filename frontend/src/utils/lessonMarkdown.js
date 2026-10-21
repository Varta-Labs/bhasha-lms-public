import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import './practiceMaterials.css'

const markdown = new MarkdownIt({ html: false, linkify: true })

export default class LessonMarkdown {
  static get isReadOnlySupported() {
    return true
  }
  constructor({ data, readOnly }) {
    this.data = data || {}
    this.readOnly = readOnly
  }
  render() {
    if (!this.readOnly) {
      this.input = document.createElement('textarea')
      this.input.className = 'bhasha-practice-markdown-input'
      this.input.setAttribute('aria-label', 'Lesson Markdown')
      this.input.value = this.data.text || ''
      return this.input
    }
    const root = document.createElement('div')
    root.className = 'bhasha-practice-markdown'
    root.innerHTML = DOMPurify.sanitize(markdown.render(this.data.text || ''))
		const tables = root.querySelectorAll('table')
		if (tables.length) {
			const hint = document.createElement('p')
			hint.className = 'bhasha-practice-table-hint'
			hint.textContent = 'Swipe sideways to see all columns.'
			tables[0].before(hint)
		}
		for (const table of tables) {
      const scroll = document.createElement('div')
      scroll.className = 'bhasha-practice-table'
      scroll.tabIndex = 0
      scroll.setAttribute('role', 'region')
      scroll.setAttribute(
        'aria-label',
        'Verb conjugation table. Scroll horizontally to see all columns.',
      )
      table.replaceWith(scroll)
      scroll.append(table)
    }
    return root
  }
  save() {
    return { text: this.input?.value ?? this.data.text }
  }
}

// The source workbook block remains intact when an instructor edits a lesson.
// Learner responses replace it with the protected PDF viewer URL.
export class BundledWorkbook {
  static get isReadOnlySupported() {
    return true
  }
  constructor({ data }) {
    this.data = data || {}
  }
  render() {
    const root = document.createElement('p')
    root.textContent =
      this.data.caption || this.data.filename || 'Practice workbook'
    return root
  }
  save() {
    return this.data
  }
}
