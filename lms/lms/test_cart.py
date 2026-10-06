import hashlib
import hmac
import json
from unittest.mock import Mock, patch

import frappe

from lms.lms.cart import (
	confirm_order_payment,
	fulfill_order,
	get_cart_payment_link,
	get_cart_summary,
	get_order_status,
	razorpay_webhook,
)
from lms.lms.test_helpers import BaseTestUtils


class CartGateway:
	def create_order(self, **kwargs):
		return {"id": "order_" + kwargs["payment"]}

	def get_payment_url(self, **kwargs):
		return "/cart-test-payment/" + kwargs["reference_docname"]


class TestCart(BaseTestUtils):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.student = self._create_user("cart.student@example.com", "Cart", "Learner", ["LMS Student"])
		self.main = self._create_course("Cart Main " + frappe.generate_hash(), "Administrator")
		category = "Cart Language " + frappe.generate_hash()
		frappe.get_doc({"doctype": "LMS Category", "category": category}).insert(ignore_permissions=True)
		self.cleanup_items.insert(0, ("LMS Category", category))
		self.main.update({"paid_course": 1, "course_price": 2000, "currency": "INR", "category": category})
		self.main.save()
		self.addon = self._create_course("Cart Pack " + frappe.generate_hash(), "Administrator")
		self.addon.update({"paid_course": 1, "course_price": 500, "currency": "INR", "category": category, "addon_for_course": self.main.name, "bundle_discount_percent": 20})
		self.addon.save()
		self.original_gateway = frappe.db.get_single_value("LMS Settings", "payment_gateway")
		self.original_gst = frappe.db.get_single_value("LMS Settings", "apply_gst")
		self.original_usd = frappe.db.get_single_value("LMS Settings", "show_usd_equivalent")
		frappe.db.set_single_value("LMS Settings", {"payment_gateway": "Razorpay", "apply_gst": 0, "show_usd_equivalent": 0})
		frappe.set_user(self.student.name)

	def tearDown(self):
		frappe.flags.data = None
		frappe.set_user("Administrator")
		# Delete the order/payment cycle and its enrollments before courses.
		for order in frappe.get_all("LMS Course Order", filters={"member": self.student.name}, fields=["name", "payment"]):
			for name in frappe.get_all("LMS Enrollment", filters={"payment": order.payment}, pluck="name"):
				frappe.delete_doc("LMS Enrollment", name, force=True)
			frappe.db.set_value("LMS Course Order", order.name, "payment", None)
			if order.payment:
				frappe.delete_doc("LMS Payment", order.payment, force=True)
			frappe.delete_doc("LMS Course Order", order.name, force=True)
		frappe.db.set_single_value("LMS Settings", {"payment_gateway": self.original_gateway, "apply_gst": self.original_gst, "show_usd_equivalent": self.original_usd})
		super().tearDown()

	def checkout(self, courses=None, coupon=None):
		courses = courses or [self.main.name, self.addon.name]
		summary = get_cart_summary(courses, "India", coupon)
		with patch("lms.lms.payments.get_controller", return_value=CartGateway()):
			url = get_cart_payment_link(courses, {
				"billing_name": "Cart Learner", "phone": "9999999999", "city": "Bengaluru", "country": "India",
			}, summary.total_amount, summary.currency, coupon)
		return frappe.get_doc("LMS Course Order", url.rsplit("/", 1)[-1])

	def webhook(self, order, *, amount=None, currency="INR", signature=True):
		payment = frappe.get_doc("LMS Payment", order.payment)
		body = json.dumps({"event": "payment.captured", "payload": {"payment": {"entity": {
			"id": "pay_cart_test", "order_id": payment.order_id, "status": "captured",
			"amount": amount if amount is not None else int(round(order.total_amount * 100)), "currency": currency,
		}}}}).encode()
		digest = hmac.new(b"cart-test-secret", body, hashlib.sha256).hexdigest() if signature else "invalid"
		request = Mock(headers={"X-Razorpay-Signature": digest})
		request.get_data.return_value = body
		with patch.dict(frappe.conf, {"bhasha_razorpay_webhook_secret": "cart-test-secret"}), patch.object(frappe.local, "request", request, create=True):
			return razorpay_webhook()

	def test_suggestion_bundle_savings_and_duplicates(self):
		summary = get_cart_summary([self.main.name], "India")
		self.assertEqual(summary.suggestions[0].course, self.addon.name)
		self.assertEqual(summary.suggestions[0].amount, 400)
		summary = get_cart_summary([self.main.name, self.addon.name, self.addon.name], "India")
		self.assertEqual(len(summary["items"]), 2)
		self.assertEqual(summary.original_amount, 2500)
		self.assertEqual(summary.discount_amount, 100)
		self.assertEqual(summary.total_amount, 2400)
		self.assertEqual(summary.suggestions, [])

	def test_addon_alone_has_no_bundle_discount(self):
		self.assertEqual(get_cart_summary([self.addon.name], "India").total_amount, 500)

	def test_only_one_addon_course_per_language(self):
		frappe.set_user("Administrator")
		other_main = self._create_course("Cart Other Main " + frappe.generate_hash(), "Administrator")
		other_main.update({"category": self.main.category, "paid_course": 1, "currency": "INR", "course_price": 2000})
		other_main.save()
		other_pack = self._create_course("Cart Other Pack " + frappe.generate_hash(), "Administrator")
		other_pack.update({"category": self.main.category, "paid_course": 1, "currency": "INR", "course_price": 500, "addon_for_course": other_main.name})
		with self.assertRaises(frappe.ValidationError):
			other_pack.save()

	def test_existing_owner_gets_same_discount_without_rebuying_main(self):
		frappe.set_user("Administrator")
		self._create_enrollment(self.student.name, self.main.name)
		frappe.set_user(self.student.name)
		summary = get_cart_summary([self.main.name, self.addon.name], "India")
		self.assertEqual(len(summary["items"]), 1)
		self.assertEqual(summary.total_amount, 400)
		self.assertEqual(summary.owned_courses[0]["course"], self.main.name)
		order = self.checkout()
		self.assertEqual(len(order.items), 1)
		self.assertEqual(order.items[0].course, self.addon.name)

	def test_gst_is_applied_after_discount(self):
		frappe.db.set_single_value("LMS Settings", "apply_gst", 1)
		summary = get_cart_summary([self.main.name, self.addon.name], "India")
		self.assertEqual(summary.gst_applied, 432)
		self.assertEqual(summary.total_amount, 2832)

	def test_no_enrollment_before_payment_and_webhook_is_safe_to_repeat(self):
		order = self.checkout()
		self.assertEqual(get_order_status(order.name)["status"], "Pending")
		self.assertFalse(frappe.db.exists("LMS Enrollment", {"member": self.student.name, "course": self.main.name}))
		frappe.set_user("Guest")
		self.webhook(order)
		self.webhook(order)
		frappe.set_user(self.student.name)
		status = get_order_status(order.name)
		self.assertEqual(status["status"], "Paid")
		self.assertTrue(all(c["enrolled"] for c in status["courses"]))
		self.assertEqual(frappe.db.count("LMS Enrollment", {"payment": order.payment}), 2)

	def test_invalid_webhook_signature_and_amount_do_not_unlock_courses(self):
		order = self.checkout()
		for values in ({"signature": False}, {"amount": 100}, {"currency": "USD"}):
			with self.assertRaises((frappe.ValidationError, frappe.PermissionError)):
				self.webhook(order, **values)
			self.assertEqual(get_order_status(order.name)["status"], "Pending")

	def test_pending_gateway_request_does_not_unlock_courses(self):
		order = self.checkout()
		with self.assertRaises(frappe.ValidationError):
			confirm_order_payment(order.name)
		with self.assertRaises(frappe.ValidationError):
			fulfill_order(order.name, order.payment)

	def test_failed_enrollment_rolls_back_the_whole_order(self):
		order = self.checkout()
		from lms.lms.doctype.lms_enrollment.lms_enrollment import LMSEnrollment
		original_insert = LMSEnrollment.insert
		def fail_second(enrollment, *args, **kwargs):
			if enrollment.course == self.addon.name:
				raise RuntimeError("Simulated enrollment failure")
			return original_insert(enrollment, *args, **kwargs)
		with patch.object(LMSEnrollment, "insert", fail_second):
			with self.assertRaises(RuntimeError):
				self.webhook(order)
		self.assertEqual(order.reload().status, "Pending")
		self.assertEqual(frappe.db.get_value("LMS Payment", order.payment, "payment_received"), 0)
		self.assertEqual(frappe.db.count("LMS Enrollment", {"payment": order.payment}), 0)
		self.webhook(order)
		self.assertEqual(order.reload().status, "Paid")

	def test_checkout_rejects_a_changed_total(self):
		with self.assertRaises(frappe.ValidationError):
			get_cart_payment_link([self.main.name, self.addon.name], {
				"billing_name": "Cart Learner", "phone": "9999999999", "city": "Bengaluru", "country": "India",
			}, 1, "INR")

	def test_order_is_private_and_immutable(self):
		order = self.checkout()
		order.total_amount = 1
		with self.assertRaises(frappe.ValidationError):
			order.save(ignore_permissions=True)
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.PermissionError):
			get_order_status(order.name)

	def test_unavailable_courses_cannot_be_purchased(self):
		frappe.db.set_value("LMS Course", self.addon.name, "published", 0)
		with self.assertRaises(frappe.ValidationError):
			self.checkout()

	def test_paid_order_cannot_enroll_in_an_unpurchased_course(self):
		order = self.checkout([self.main.name])
		self.webhook(order)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc({"doctype": "LMS Enrollment", "member": self.student.name, "course": self.addon.name, "payment": order.payment}).insert(ignore_permissions=True)

	def test_confirmed_snapshot_survives_catalog_changes(self):
		order = self.checkout()
		frappe.db.set_value("LMS Course", self.addon.name, {"course_price": 999, "published": 0})
		self.webhook(order)
		self.assertEqual(order.reload().total_amount, 2400)
		self.assertTrue(get_order_status(order.name)["courses"][1]["enrolled"])

	def test_fixed_coupon_price_is_applied_once_and_does_not_stack(self):
		frappe.set_user("Administrator")
		coupon = frappe.get_doc({"doctype": "LMS Coupon", "code": "CART-" + frappe.generate_hash(), "enabled": 1,
			"discount_type": "Fixed Amount", "fixed_amount_discount": 2200,
			"applicable_items": [{"reference_doctype": "LMS Course", "reference_name": c} for c in (self.main.name, self.addon.name)]}).insert()
		self.cleanup_items.append(("LMS Coupon", coupon.name))
		frappe.set_user(self.student.name)
		summary = get_cart_summary([self.main.name, self.addon.name], "India", coupon.code)
		self.assertEqual(summary.discount_amount, 300)
		self.assertEqual(summary.total_amount, 2200)
		self.assertEqual(summary.coupon, coupon.name)
		order = self.checkout(coupon=coupon.code)
		self.webhook(order)
		self.webhook(order)
		self.assertEqual(coupon.reload().redemption_count, 1)
