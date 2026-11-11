import frappe


def execute():
	"""Remove the two Kevin Test reviews from the Marathi courses."""
	for course, review in (
		("marathi-for-everyday-conversations", "uc7867inut"),
		("marathi-addons", "proh1rtkbb"),
	):
		frappe.db.delete("LMS Course Review", {"name": review, "course": course})
