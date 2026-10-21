"""Payment recovery checks runnable without a Frappe site or payment credentials."""

import importlib.util
import sys
import types
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

from requests.exceptions import HTTPError


class TestCartReconciliation(unittest.TestCase):
	def setUp(self):
		frappe = types.ModuleType("frappe")
		frappe._ = lambda text: text
		frappe.whitelist = lambda **kwargs: lambda function: function
		frappe.PermissionError = PermissionError
		frappe.session = types.SimpleNamespace(user="learner@example.com")
		frappe.get_doc = Mock()
		frappe.db = Mock()
		frappe.db.sql.return_value = []
		frappe.throw = Mock(side_effect=lambda message, error=ValueError: self.raise_error(error, message))
		utils = types.ModuleType("frappe.utils")
		utils.cint = lambda value: int(value or 0)
		utils.flt = float
		utils.fmt_money = Mock()
		lms_utils = types.ModuleType("lms.lms.utils")
		for name in ("apply_coupon", "apply_gst", "check_multicurrency", "get_lms_route"):
			setattr(lms_utils, name, Mock())
		# Load the actual cart implementation with only its framework boundary stubbed.
		spec = importlib.util.spec_from_file_location("cart_under_test", Path(__file__).parent / "lms/cart.py")
		self.cart = importlib.util.module_from_spec(spec)
		with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": utils, "lms.lms.utils": lms_utils}):
			spec.loader.exec_module(self.cart)
		self.frappe = frappe
		self.order = types.SimpleNamespace(
			name="local-order", member=frappe.session.user, status="Pending", payment="local-payment",
			currency="INR", total_amount=Decimal("28.32"),
			items=[types.SimpleNamespace(course="main", title="Main"), types.SimpleNamespace(course="addon", title="Addon")],
			reload=Mock(),
		)
		self.payment = types.SimpleNamespace(name="local-payment", order_id="order_saved")
		frappe.get_doc.side_effect = lambda doctype, name, **kwargs: self.order if doctype == "LMS Course Order" else self.payment
		self.cart.fetch_razorpay_resource = Mock(return_value={"items": []})
		self.cart.capture_razorpay_payment = Mock(return_value=self.entity())
		self.cart.fulfill_order = Mock(side_effect=lambda *args: setattr(self.order, "status", "Paid"))

	@staticmethod
	def raise_error(error, message):
		raise error(message)

	def entity(self, **values):
		return {"id": "pay_captured", "order_id": "order_saved", "amount": 2832,
			"currency": "INR", "status": "captured", **values}

	def test_recovers_capture_without_integration_request_or_callback(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity()]}
		status = self.cart.get_order_status(self.order.name)
		self.assertEqual(status["status"], "Paid")
		self.cart.fulfill_order.assert_called_once_with("local-order", "local-payment", "pay_captured")
		self.cart.fetch_razorpay_resource.assert_called_once_with("orders/order_saved/payments")
		self.order.reload.assert_called_once()

	def test_next_check_recovers_a_delayed_capture(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		self.cart.capture_razorpay_payment.return_value = self.entity(status="authorized")
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Pending")
		self.cart.fulfill_order.assert_not_called()
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity()]}
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")

	def test_empty_failed_created_and_refunded_attempts_do_not_unlock_access(self):
		for entities in ([], [self.entity(status="failed")], [self.entity(status="created")], [self.entity(status="refunded")]):
			with self.subTest(entities=entities):
				self.cart.fetch_razorpay_resource.return_value = {"items": entities}
				self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Pending")
		self.cart.fulfill_order.assert_not_called()
		self.cart.capture_razorpay_payment.assert_not_called()

	def test_authorized_payment_is_captured_before_fulfillment(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")
		self.cart.capture_razorpay_payment.assert_called_once_with("pay_captured", 2832, "INR")
		self.cart.fulfill_order.assert_called_once_with("local-order", "local-payment", "pay_captured")

	def test_mismatched_authorizations_are_never_captured(self):
		for values in ({"order_id": "order_other"}, {"amount": 1}, {"currency": "USD"}):
			with self.subTest(values=values):
				self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized", **values)]}
				with self.assertRaises(ValueError):
					self.cart.get_order_status(self.order.name)
		self.cart.capture_razorpay_payment.assert_not_called()
		self.cart.fulfill_order.assert_not_called()

	def test_existing_capture_takes_priority_over_another_authorization(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(id="pay_other", status="authorized"), self.entity()]}
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")
		self.cart.capture_razorpay_payment.assert_not_called()

	def test_concurrent_capture_is_verified_after_capture_request_error(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		self.cart.capture_razorpay_payment.side_effect = HTTPError("Already captured")
		self.cart.fetch_razorpay_payment = Mock(return_value=self.entity())
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")
		self.cart.fetch_razorpay_payment.assert_called_once_with("pay_captured")

	def test_failed_capture_without_confirmed_readback_does_not_unlock_access(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		self.cart.capture_razorpay_payment.side_effect = HTTPError("Capture failed")
		self.cart.fetch_razorpay_payment = Mock(return_value=self.entity(status="authorized"))
		with self.assertRaises(HTTPError):
			self.cart.get_order_status(self.order.name)
		self.cart.fulfill_order.assert_not_called()

	def test_capture_response_must_match_original_payment_and_amount(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		for values in ({"id": "pay_other"}, {"amount": 1}, {"currency": "USD"}, {"order_id": "order_other"}):
			with self.subTest(values=values):
				self.cart.capture_razorpay_payment.return_value = self.entity(**values)
				with self.assertRaises(ValueError):
					self.cart.get_order_status(self.order.name)
		self.cart.fulfill_order.assert_not_called()

	def test_superseded_authorization_does_not_charge_for_owned_courses(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		self.frappe.db.sql.return_value = [("main",)]
		with self.assertRaisesRegex(ValueError, "already in your account"):
			self.cart.get_order_status(self.order.name)
		self.cart.capture_razorpay_payment.assert_not_called()
		self.cart.fulfill_order.assert_not_called()
		self.frappe.get_doc.assert_any_call("User", self.order.member, for_update=True)

	def test_order_paid_while_waiting_for_capture_lock_is_not_captured_again(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="authorized")]}
		paid_order = types.SimpleNamespace(status="Paid")
		self.frappe.get_doc.side_effect = lambda doctype, name, **kwargs: (
			paid_order if doctype == "LMS Course Order" and kwargs.get("for_update")
			else self.order if doctype == "LMS Course Order" else self.payment
		)
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")
		self.cart.capture_razorpay_payment.assert_not_called()
		self.cart.fulfill_order.assert_not_called()

	def test_finds_capture_after_failed_attempt(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(status="failed"), self.entity()]}
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")

	def test_wrong_order_amount_or_currency_is_rejected(self):
		for values in ({"order_id": "order_other"}, {"amount": 1}, {"currency": "USD"}):
			with self.subTest(values=values):
				self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(**values)]}
				with self.assertRaises(ValueError):
					self.cart.get_order_status(self.order.name)
		self.cart.fulfill_order.assert_not_called()

	def test_capture_without_payment_id_is_not_accepted(self):
		self.cart.fetch_razorpay_resource.return_value = {"items": [self.entity(id=None)]}
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Pending")
		self.cart.fulfill_order.assert_not_called()

	def test_another_learner_cannot_trigger_gateway_lookup(self):
		self.frappe.session.user = "other@example.com"
		with self.assertRaises(PermissionError):
			self.cart.get_order_status(self.order.name)
		self.cart.fetch_razorpay_resource.assert_not_called()
		self.cart.fulfill_order.assert_not_called()

	def test_paid_orders_do_not_query_gateway_or_fulfill_again(self):
		self.order.status = "Paid"
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Paid")
		self.cart.fetch_razorpay_resource.assert_not_called()
		self.cart.fulfill_order.assert_not_called()

	def test_order_without_gateway_id_stays_pending(self):
		self.payment.order_id = None
		self.assertEqual(self.cart.get_order_status(self.order.name)["status"], "Pending")
		self.cart.fetch_razorpay_resource.assert_not_called()

	def test_gateway_outage_does_not_fulfill_order(self):
		self.cart.fetch_razorpay_resource.side_effect = ConnectionError("Gateway unavailable")
		with self.assertRaises(ConnectionError):
			self.cart.get_order_status(self.order.name)
		self.assertEqual(self.order.status, "Pending")
		self.cart.fulfill_order.assert_not_called()


if __name__ == "__main__":
	unittest.main()
