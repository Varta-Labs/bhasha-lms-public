import frappe
from frappe import _
from frappe.model.document import Document


class LMSCourseOrder(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(_("Course orders are purchase records and cannot be edited."))

	def on_payment_authorized(self, payment_status):
		if payment_status in ("Authorized", "Completed"):
			from lms.lms.cart import confirm_order_payment
			confirm_order_payment(self.name)
