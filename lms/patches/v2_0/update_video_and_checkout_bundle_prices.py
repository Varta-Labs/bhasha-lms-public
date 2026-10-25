"""Apply the revised catalog and checkout offer without replacing course content."""

import frappe


def execute():
	for language in ("kannada", "hindi", "tamil", "telugu", "malayalam", "marathi"):
		for suffix, values in (
			("for-everyday-conversations", {"course_price": 2499}),
			("addons", {"course_price": 1999, "bundle_discount_percent": 74.987494}),
		):
			name = f"{language}-{suffix}"
			if frappe.db.exists("LMS Course", name):
				frappe.db.set_value(
					"LMS Course", name, {**values, "paid_course": 1, "currency": "INR"},
					update_modified=False,
				)
