# Copyright (c) 2025, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint



class SampleInward(Document):

    @frappe.whitelist()
    def validate_material_rows(self):
        qty = int(self.quantity or 0) 

        self.set("material_details", [])
        for i in range(qty):
            self.append("material_details", {})

        return qty
#**************************************************************************************************
    @frappe.whitelist()
    def update_material_rows(self):
        qty = int(self.quantity or 0)
        existing_rows = len(self.material_details)

        if qty > existing_rows:
            for i in range(existing_rows, qty):
                self.append("material_details", {})
        elif qty < existing_rows:
            for i in range(existing_rows - qty):
                self.material_details.pop()
        return qty
#**************************************************************************************************
    def before_save(self):
        self.get_material_details()
        self.set_sample_ids()
        self.set_test_ids()

    def get_material_details(self):
        company = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"
        last = int((frappe.db.get_value("Company", company, "custom_sample_counter") or "S0").replace("S", ""))
        updated = False
        spec_map = {t.material_specification: t.sample_id for t in self.test_on_sample if t.sample_id}
        for mat in self.material_details:
            sid = spec_map.get(mat.material_specification)            
            if not sid:
                last += 1
                sid = f"S{last}"
                spec_map[mat.material_specification] = sid
                updated = True
            mat.counter = sid
            for test in self.test_on_sample:
                if test.material_specification == mat.material_specification and not test.sample_id:
                    test.sample_id = sid
                    test.heat_number = mat.heat_number
                    test.material_shape = mat.material_shape
        if updated:
            frappe.db.set_value("Company", company, "custom_sample_counter", f"S{last}")

#**************************************************************************************************

    def set_sample_ids(self):
        company_name = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"

        sample_ids = [row.sample_id for row in self.test_on_sample if row.sample_id]

        if sample_ids:
            max_num = max(int(s.replace("S", "")) for s in sample_ids if s.startswith("S"))
            frappe.db.set_value("Company", company_name, "custom_sample_counter", f"S{max_num}")
    

#**************************************************************************************************
    def set_test_ids(self):
        company_name = "DELTAA METALLIX SOLUTIONS PRIVATE LIMITED"
        last = frappe.db.get_value("Company", company_name, "custom_test_counter") or "0"
        count = int(last) + 1 
        for row in self.test_on_sample:
            if not row.test_id:
                row.test_id = str(count)
                count += 1
        frappe.db.set_value("Company", company_name, "custom_test_counter", str(count - 1))

#**********************************************************************************************
    def on_submit(self):
        self.show_massage()
    def show_massage(self):
        for row in self.test_on_sample:
            new_doc = frappe.new_doc("Lab Analyst")
            new_doc.inward_number = self.name
            new_doc.test_group = row.test_group
            new_doc.material_shape = row.material_shape
            new_doc.heat_number = row.heat_number
            new_doc.test_method = row.test_method
            new_doc.customer_specification = row.customer_specification
            new_doc.test_description = row.test_description
            new_doc.sample_description = row.sample_description
            new_doc.child_table_id = row.name
            new_doc.document_id = row.test_id 

            if row.sample_id and row.test_id:
                new_doc.document_id = f"{row.sample_id}/{row.test_id}"
            else:
                new_doc.document_id = row.test_id or row.sample_id or ""
            new_doc.save()
            
    @frappe.whitelist()        
    def get_material_sample_details(self):
        self.test_on_sample = []

        for mat_row in self.material_details:
            if mat_row.material_specification:
                item_doc = frappe.get_doc("Item", mat_row.material_specification)

                for sample_row in item_doc.custom_material_sample_details:
                    # frappe.msgprint(str(sample_row.test_method))
                    des_price=frappe.get_value("Test Description", sample_row.test_description, "rate")

                    self.append("test_on_sample", {
                        "material_specification": mat_row.material_specification,
                        "test_group": sample_row.test_group,
                        "test_method": sample_row.test_method,
                        "test_description": sample_row.test_description,   
                        "price":des_price,
                        "material_shape": sample_row.material_shape,
                        "discipline": sample_row.discipline,
                        "group": sample_row.group
                    })
                    
        return self

