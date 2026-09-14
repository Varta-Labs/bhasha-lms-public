import frappe


def execute():
	"""Apply catalog thumbnails without reimporting existing course content."""
	for language, extension in (("hindi", "png"), ("kannada", "jpg")):
		course_name = f"{language}-for-everyday-conversations"
		if frappe.db.exists("LMS Course", course_name):
			frappe.db.set_value(
				"LMS Course",
				course_name,
				"image",
				f"/assets/lms/images/course-thumbnails/{language}-course-thumbnail.{extension}",
				update_modified=False,
			)
