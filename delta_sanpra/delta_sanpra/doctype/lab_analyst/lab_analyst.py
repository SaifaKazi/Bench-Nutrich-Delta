# # Copyright (c) 2025, Sanpra Software Solution and contributors
# # For license information, please see license.txt

# 	def on_submit(self):
# 		self.get_child_table_id()

# 	def get_child_table_id(self):
# 		inward_doc = frappe.get_doc("Sample Inward", self.inward_number)
# 		inward_number = inward_doc.name

# 		for row in inward_doc.test_on_sample: 
# 			if row.name == self.child_table_id:
# 				frappe.db.set_value("Test On sample", row.name, "status", "Complete")
			
# 			# frappe.msgprint(f"Test Group: {row.test_group} | Status: {row.status}")
# 			# frappe.msgprint("hi")

import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import get_file
from openpyxl import load_workbook
import io

class LabAnalyst(Document):
    @frappe.whitelist()
    def create_rate_chart_from_file(self):
        if not self.name:
            frappe.throw("Please save the document first.")

        file_url = self.upload_excel_file or self.upload_pdf_file
        if not file_url:
            self.set("test_details", [])
            self.save(ignore_permissions=True)
            # frappe.msgprint("File cleared — test details removed.")
            return

        file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
        if not file_name:
            frappe.throw("File not found in the system.")

        file_doc = frappe.get_doc("File", file_name)
        file_content = file_doc.get_content()

        if file_url.lower().endswith((".xlsx", ".xls", ".xlsm")):
            sheet = load_workbook(io.BytesIO(file_content), data_only=True).active
            self.test_details = []
            for r in range(2, sheet.max_row + 1):
                p, v = sheet.cell(r, 1).value, sheet.cell(r, 2).value
                if p and v:
                    self.append("test_details", {"parameter": str(p), "value": str(v)})
            # frappe.msgprint("Excel data imported successfully.")

        elif file_url.lower().endswith(".pdf"):
            self.set("test_details", [])
            # frappe.msgprint(f"PDF '{file_doc.file_name}' uploaded successfully.")

        self.save(ignore_permissions=True)

#******************************************************************************************
    def on_submit(self):
        self.get_child_table_id()

    def get_child_table_id(self):
        inward_doc = frappe.get_doc("Sample Inward", self.inward_number)
        inward_number = inward_doc.name

        for row in inward_doc.test_on_sample:
            if row.name == self.child_table_id:
                frappe.db.set_value("Test On sample", row.name, "status", "Complete")
              
