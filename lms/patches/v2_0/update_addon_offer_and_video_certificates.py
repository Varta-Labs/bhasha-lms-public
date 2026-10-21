"""Update the catalog offer without replacing curriculum or learner progress."""

import frappe


def execute():
	for language in ("kannada", "hindi", "tamil", "telugu", "malayalam", "marathi"):
		main = f"{language}-for-everyday-conversations"
		if frappe.db.exists("LMS Course", main):
			frappe.db.set_value(
				"LMS Course", main,
				{"enable_certification": 1, "paid_certificate": 0},
				update_modified=False,
			)
		pack = f"{language}-addons"
		if frappe.db.exists("LMS Course", pack):
			frappe.db.set_value(
				"LMS Course", pack,
				{"course_price": 999, "bundle_discount_percent": 10.010010},
				update_modified=False,
			)
