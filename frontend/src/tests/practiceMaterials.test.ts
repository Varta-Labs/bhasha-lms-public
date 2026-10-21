import { describe, expect, it } from 'vitest'
import LessonMarkdown, { BundledWorkbook } from '@/utils/lessonMarkdown'

describe('practice materials', () => {
  it('renders readable, keyboard-scrollable Markdown tables and escapes HTML', () => {
    const tool = new LessonMarkdown({
      readOnly: true,
      data: {
        text: 'The verb **aaDu** means **to play**\n\n## Simple Past\n\n| Pronoun | Past | Meaning |\n| --- | --- | --- |\n| naanu | aaDide | I played |\n\n<script>alert(1)</script>',
      },
    })
    const root = tool.render()
    expect(root.querySelector('h2')?.textContent).toBe('Simple Past')
    expect(root.querySelectorAll('th')).toHaveLength(3)
    expect(root.querySelectorAll('td')).toHaveLength(3)
    expect(
      root.querySelector('[role="region"]')?.getAttribute('tabindex'),
    ).toBe('0')
    expect(root.querySelector('script')).toBeNull()
    expect(root.querySelector('strong')?.textContent).toBe('aaDu')
  })

  it('preserves Markdown source and the bundled PDF when an instructor saves', () => {
    const tool = new LessonMarkdown({
      readOnly: false,
      data: { text: '| a | b |' },
    })
    const input = tool.render() as HTMLTextAreaElement
    input.value += '\n| c | d |'
    expect(tool.save().text).toBe('| a | b |\n| c | d |')
    const data = {
      filename: 'kannada-verb-conjugation-workbook.pdf',
      caption: 'Practice workbook',
    }
    const workbook = new BundledWorkbook({ data })
    expect(workbook.render().textContent).toBe('Practice workbook')
    expect(workbook.save()).toEqual(data)
  })
})
