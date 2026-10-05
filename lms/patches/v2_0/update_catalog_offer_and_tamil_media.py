import frappe


def execute():
	"""Update catalog pricing and Tamil media without reimporting lessons."""
	for language in ("hindi", "kannada", "tamil", "telugu", "malayalam", "marathi"):
		course_name = f"{language}-for-everyday-conversations"
		if not frappe.db.exists("LMS Course", course_name):
			continue
		values = {"paid_course": 1, "course_price": 1999, "currency": "INR"}
		if language == "tamil":
			values.update(
				{
					"image": "/assets/lms/images/course-thumbnails/tamil-video-thumbnail.png",
					"video_link": "https://player.vimeo.com/video/1227264908",
				}
			)
		frappe.db.set_value("LMS Course", course_name, values, update_modified=False)
