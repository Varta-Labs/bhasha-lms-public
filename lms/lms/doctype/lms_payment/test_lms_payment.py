# Copyright (c) 2023, Frappe and Contributors
# See license.txt

import json
from unittest.mock import patch

import frappe

from lms.lms.payments import get_payment_link, get_razorpay_checkout_url
from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import update_payment_record


class DummyPaymentController:
	def create_order(self, **kwargs):
		return {"id": "order_test"}

	def get_payment_url(self, **kwargs):
		return f"/payment-url/{kwargs['payment']}"


class EmptyOrderPaymentController:
	def create_order(self, **kwargs):
		return None

	def get_payment_url(self, **kwargs):
		return f"/payment-url/{kwargs['payment']}"


class TestLMSPayment(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user(
			"payment-student@example.com", "Payment", "Student", ["LMS Student"]
		)
		self.instructor = self._create_user(
			"payment-instructor@example.com",
			"Payment",
			"Instructor",
			["Moderator", "Course Creator", "Batch Evaluator"],
		)
		frappe.db.set_single_value("LMS Settings", "payment_gateway", "Razorpay")
		frappe.set_user(self.student.email)

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def test_get_payment_link_rechecks_billing_access(self):
		course = self._create_paid_course()
		self._create_paid_lms_payment(course.name, payment_received=1)
		self._create_enrollment(self.student.email, course.name)

		with self.assertRaises(frappe.ValidationError):
			get_payment_link(
				doctype="LMS Course",
				docname=course.name,
				address=self._billing_address(),
				payment_for_certificate=0,
				country="India",
			)

	def test_razorpay_checkout_url_uses_lms_wrapper(self):
		url = get_razorpay_checkout_url(
			"https://lms.localhost/razorpay_checkout?token=razorpay-token"
		)

		self.assertEqual(url, "/lms_razorpay_checkout?token=razorpay-token")

	def test_update_payment_record_uses_matching_payment_integration_request(self):
		course = self._create_paid_course()
		first_payment = self._create_paid_lms_payment(course.name, payment_received=0)
		second_payment = self._create_paid_lms_payment(course.name, payment_received=0)

		self._create_integration_request(course.name, first_payment.name, "pay_first")
		self._create_integration_request(course.name, second_payment.name, "pay_second")

		frappe.flags.data = frappe._dict({"payment": first_payment.name})
		update_payment_record("LMS Course", course.name)

		first_payment.reload()
		second_payment.reload()

		self.assertEqual(first_payment.payment_received, 1)
		self.assertEqual(first_payment.payment_id, "pay_first")
		self.assertEqual(second_payment.payment_received, 0)

	def test_get_payment_link_creates_payment_and_delegates_to_gateway(self):
		course = self._create_paid_course()

		with patch("lms.lms.payments.get_controller", return_value=DummyPaymentController()):
			url = get_payment_link(
				doctype="LMS Course",
				docname=course.name,
				address=self._billing_address(),
				payment_for_certificate=0,
				country="India",
			)

		payment = frappe.get_last_doc(
			"LMS Payment",
			filters={
				"member": self.student.email,
				"payment_for_document_type": "LMS Course",
				"payment_for_document": course.name,
			},
		)

		self.assertEqual(url, f"/payment-url/{payment.name}")
		self.assertEqual(payment.payment_received, 0)
		self.assertEqual(payment.order_id, None)

	def test_get_payment_link_rejects_empty_razorpay_order_response(self):
		course = self._create_paid_course()

		with patch("lms.lms.payments.get_controller", return_value=EmptyOrderPaymentController()):
			with self.assertRaises(frappe.ValidationError) as context:
				get_payment_link(
					doctype="LMS Course",
					docname=course.name,
					address=self._billing_address(),
					payment_for_certificate=0,
					country="India",
				)

		self.assertIn("Unable to create a Razorpay order", str(context.exception))

	def _create_paid_course(self):
		frappe.set_user("Administrator")
		course = self._create_course(f"Paid Course {frappe.generate_hash()}", self.instructor.email)
		course.paid_course = 1
		course.course_price = 100
		course.currency = "INR"
		course.save()
		frappe.set_user(self.student.email)
		return course

	def _create_paid_lms_payment(self, course, payment_received=0):
		payment = frappe.new_doc("LMS Payment")
		payment.update(
			{
				"member": self.student.email,
				"billing_name": "Payment Student",
				"address": self._create_address(),
				"amount": 100,
				"currency": "INR",
				"source": self._create_source(),
				"payment_for_document_type": "LMS Course",
				"payment_for_document": course,
				"payment_received": payment_received,
				"member_consent": 1,
			}
		)
		payment.insert(ignore_permissions=True)
		self.cleanup_items.append(("LMS Payment", payment.name))
		return payment

	def _create_integration_request(self, course, payment, payment_id):
		request = frappe.new_doc("Integration Request")
		request.update(
			{
				"integration_request_service": "Razorpay",
				"status": "Queued",
				"reference_doctype": "LMS Course",
				"reference_docname": course,
				"data": json.dumps(
					{
						"payment": payment,
						"payment_gateway": "Razorpay",
						"razorpay_payment_id": payment_id,
						"order_id": f"order_{payment_id}",
					}
				),
			}
		)
		request.owner = self.student.email
		request.insert(ignore_permissions=True)
		self.cleanup_items.append(("Integration Request", request.name))
		return request

	def _billing_address(self):
		return {
			"billing_name": "Payment Student",
			"address_line1": "Street 1",
			"address_line2": "",
			"city": "Bengaluru",
			"state": "Karnataka",
			"country": "India",
			"pincode": "560001",
			"phone": "9999999999",
			"source": self._create_source(),
			"gstin": "",
			"pan": "",
			"member_consent": 1,
		}

	def _create_source(self):
		if not frappe.db.exists("LMS Source", "Payment Test"):
			source = frappe.new_doc("LMS Source")
			source.source = "Payment Test"
			source.insert(ignore_permissions=True)
			self.cleanup_items.append(("LMS Source", source.name))
		return "Payment Test"

	def _create_address(self):
		address = frappe.new_doc("Address")
		address.update(
			{
				"address_title": "Payment Student",
				"address_type": "Billing",
				"address_line1": "Street 1",
				"city": "Bengaluru",
				"state": "Karnataka",
				"country": "India",
				"pincode": "560001",
				"email_id": self.student.email,
			}
		)
		address.insert(ignore_permissions=True)
		self.cleanup_items.append(("Address", address.name))
		return address.name
