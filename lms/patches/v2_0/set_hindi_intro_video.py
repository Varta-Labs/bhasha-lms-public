import frappe


def execute():
	"""Update the Hindi preview without reimporting its curriculum."""
	course_name = "hindi-for-everyday-conversations"
	if frappe.db.exists("LMS Course", course_name):
		frappe.db.set_value(
			"LMS Course",
			course_name,
			"video_link",
			"https://player.vimeo.com/video/1225230901",
			update_modified=False,
		)
