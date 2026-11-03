import frappe


def execute():
	"""Update course thumbnails and introductions without reimporting lessons."""
	for language, video_id in (
		("telugu", "1240276787"),
		("malayalam", "1240278535"),
		("marathi", "1240319159"),
	):
		course_name = f"{language}-for-everyday-conversations"
		if not frappe.db.exists("LMS Course", course_name):
			continue
		frappe.db.set_value(
			"LMS Course",
			course_name,
			{
				"image": f"/assets/lms/images/course-thumbnails/{language}-video-thumbnail.png",
				"video_link": f"https://player.vimeo.com/video/{video_id}",
			},
			update_modified=False,
		)
