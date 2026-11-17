"""Course removal and refund checks runnable without a Frappe site."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch


class TestCourseRefund(unittest.TestCase):
	def setUp(self):
		frappe = types.ModuleType("frappe")
		frappe._ = lambda text: text
		frappe.whitelist = lambda **kwargs: lambda function: function
		frappe.PermissionError = PermissionError
		frappe.session = types.SimpleNamespace(user="manager@example.com")
		frappe.only_for = Mock()
		frappe.get_doc = Mock(return_value=types.SimpleNamespace(name="enr-1", member="learner@example.com", course="hindi"))
		frappe.get_all = Mock(return_value=[])
		frappe.delete_doc = Mock()
		frappe.db = Mock()
		frappe.db.sql.return_value = []
		frappe.throw = Mock(side_effect=lambda message, error=ValueError: (_ for _ in ()).throw(error(message)))
		utils = types.ModuleType("frappe.utils")
		utils.cint = lambda value: int(value or 0)
		utils.flt = float
		utils.fmt_money = Mock()
		utils.now_datetime = Mock(return_value="2026-11-17 10:00:00")
		lms_utils = types.ModuleType("lms.lms.utils")
		for name in ("apply_coupon", "apply_gst", "check_multicurrency", "get_lms_route"):
			setattr(lms_utils, name, Mock())
		self.update_program_progress = Mock()
		enrollment_module = types.ModuleType("lms.lms.doctype.lms_enrollment.lms_enrollment")
		enrollment_module.update_program_progress = self.update_program_progress
		self.modules = {
			"frappe": frappe, "frappe.utils": utils, "lms.lms.utils": lms_utils,
			"lms.lms.doctype.lms_enrollment.lms_enrollment": enrollment_module,
		}
		spec = importlib.util.spec_from_file_location("cart_under_test", Path(__file__).parent / "lms/cart.py")
		self.cart = importlib.util.module_from_spec(spec)
		with patch.dict(sys.modules, self.modules):
			spec.loader.exec_module(self.cart)
		self.frappe = frappe
		self.refund = {
			"refunded": 1, "refunded_on": "2026-11-17 10:00:00",
			"refunded_by": "manager@example.com", "refund_reference": "rfnd_123",
		}

	def remove(self, **kwargs):
		with patch.dict(sys.modules, self.modules):
			return self.cart.remove_course_enrollment("enr-1", **kwargs)

	def test_only_moderators_can_remove(self):
		self.frappe.only_for.side_effect = PermissionError("Not permitted")
		with self.assertRaises(PermissionError):
			self.remove()
		self.frappe.delete_doc.assert_not_called()

	def test_remove_without_refund_leaves_payments_untouched(self):
		self.assertEqual(self.remove(), {"refunded": False})
		self.frappe.only_for.assert_called_once_with(("Moderator", "System Manager"))
		self.frappe.delete_doc.assert_called_once_with("LMS Enrollment", "enr-1", ignore_permissions=True)
		self.frappe.db.set_value.assert_not_called()
		self.update_program_progress.assert_called_once_with("learner@example.com")

	def test_refund_marks_the_cart_order_line(self):
		self.frappe.db.sql.return_value = ["item-1"]
		self.assertEqual(self.remove(refunded="1", refund_reference="  rfnd_123 "), {"refunded": True})
		self.assertEqual(self.frappe.db.sql.call_args.args[1], {"member": "learner@example.com", "course": "hindi"})
		self.frappe.db.set_value.assert_called_once_with("LMS Course Order Item", "item-1", self.refund)
		self.frappe.delete_doc.assert_called_once()

	def test_refund_marks_a_single_course_payment(self):
		self.frappe.get_all.return_value = ["pay-1"]
		self.remove(refunded=1, refund_reference="rfnd_123")
		filters = self.frappe.get_all.call_args.kwargs["filters"]
		self.assertEqual(filters["payment_for_document_type"], "LMS Course")
		self.assertEqual(filters["refunded"], 0)
		self.frappe.db.set_value.assert_called_once_with("LMS Payment", "pay-1", self.refund)

	def test_refund_without_a_purchase_keeps_the_student(self):
		with self.assertRaises(ValueError):
			self.remove(refunded=1)
		self.frappe.db.set_value.assert_not_called()
		self.frappe.delete_doc.assert_not_called()

	def test_blank_reference_is_stored_as_empty(self):
		self.frappe.db.sql.return_value = ["item-1"]
		self.remove(refunded=1, refund_reference="   ")
		self.assertIsNone(self.frappe.db.set_value.call_args.args[2]["refund_reference"])

	def test_refunded_order_line_cannot_unlock_an_enrollment(self):
		self.frappe.db.get_value.return_value = types.SimpleNamespace(
			member="learner@example.com", payment_received=1,
			payment_for_document_type="LMS Course Order", payment_for_document="order-1",
		)
		self.frappe.db.exists.return_value = True
		self.cart.has_course_order_payment("pay-1", "learner@example.com", "hindi")
		self.assertIn(call("LMS Course Order Item", {
			"parent": "order-1", "parenttype": "LMS Course Order", "course": "hindi", "refunded": 0,
		}), self.frappe.db.exists.call_args_list)


if __name__ == "__main__":
	unittest.main()
