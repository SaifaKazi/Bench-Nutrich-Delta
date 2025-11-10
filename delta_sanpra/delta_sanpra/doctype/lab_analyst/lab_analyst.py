# # Copyright (c) 2025, Sanpra Software Solution and contributors
# # For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import get_file
from openpyxl import load_workbook
import io
import pdfplumber

class LabAnalyst(Document):

    @frappe.whitelist()
    def create_rate_chart_from_excel(self):
        if not self.upload_excel_file:
            frappe.throw("Please upload an Excel file first.")

        file_doc = frappe.get_doc("File", {"file_url": self.upload_excel_file})
        sheet = load_workbook(io.BytesIO(file_doc.get_content()), data_only=True).active
        self.test_details = []

        for r in range(2, sheet.max_row + 1):
            p, v = sheet.cell(r, 1).value, sheet.cell(r, 2).value
            if p and v:
                self.append("test_details", {"parameter": str(p), "value": str(v)})
        self.save(ignore_permissions=True)

    @frappe.whitelist()
    def create_rate_chart_from_pdf(self):
        if not self.upload_pdf_file:
            frappe.throw("Please upload a PDF file first.")

        file_doc = frappe.get_doc("File", {"file_url": self.upload_pdf_file})
        pdf = pdfplumber.open(io.BytesIO(file_doc.get_content()))
        self.test_details = []
        for page in pdf.pages:
            lines = []
            table = page.extract_table()
            if table and len(table) > 1:
                lines = [row[:2] for row in table[1:] if len(row) >= 2]
            else:
                text = page.extract_text() or ""
                lines = [l.split(":", 1) if ":" in l else l.rsplit(None, 1) 
                         for l in text.split("\n") if l.strip()]
            for row in lines:
                if len(row) == 2 and row[0] and row[1]:
                    self.append("test_details", {
                        "parameter": row[0].strip(),
                        "value": row[1].strip()
                    })
        pdf.close()
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
              
