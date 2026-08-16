import frappe


LEGACY_COURSE_TITLE = "A guide to Frappe Learning"
BHASHA_COURSE_TITLE = "A guide to Bhasha"


def execute():
	"""Update the demo records installed before the Bhasha rebrand."""
	course = frappe.db.get_value(
		"LMS Course",
		{"title": LEGACY_COURSE_TITLE},
		["name", "short_introduction", "description"],
		as_dict=True,
	)
	if course:
		frappe.db.set_value(
			"LMS Course",
			course.name,
			{
				"title": BHASHA_COURSE_TITLE,
				"short_introduction": (course.short_introduction or "").replace(
					"Frappe Learning", "Bhasha"
				),
				"description": (course.description or "")
				.replace("Frappe Learning", "Bhasha")
				.replace("https://docs.frappe.io/learning", "https://bhasha.io"),
			},
		)

		for lesson in frappe.get_all("Course Lesson", {"course": course.name}, ["name", "title", "content"]):
			frappe.db.set_value(
				"Course Lesson",
				lesson.name,
				{
					"title": (lesson.title or "").replace("Frappe Learning", "Bhasha"),
					"content": (lesson.content or "").replace("Frappe Learning", "Bhasha"),
				},
			)

	for question in frappe.get_all(
		"LMS Question", {"question": ["like", "%Frappe Learning%"]}, ["name", "question"]
	):
		frappe.db.set_value(
			"LMS Question", question.name, "question", question.question.replace("Frappe Learning", "Bhasha")
		)

	frappe.db.set_value(
		"LMS Quiz", {"title": "Do you know Frappe Learning?"}, "title", "Do you know Bhasha?"
	)
