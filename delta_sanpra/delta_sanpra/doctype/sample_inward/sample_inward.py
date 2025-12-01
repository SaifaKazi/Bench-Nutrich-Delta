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
        # if existing_rows > qty:
        #     frappe.throw(("You cannot add more than {0} Material Details rows because Quantity is {0}").format(qty)
        #     )
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
        self.get_sample_id_and_test_id()
        self.set_sticker_print_from_test_on_sample()

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
    
#**************************************************************************************************
    def get_sample_id_and_test_id(self):
        for row in self.test_on_sample:
            if row.sample_id and row.test_id:
                row.sample_idtest_id = f"{row.sample_id}/{row.test_id}"
            else:
                row.sample_idtest_id = row.test_id or row.sample_id or ""
#**************************************************************************************************
    def set_sticker_print_from_test_on_sample(self):
        self.sticker_print = []
        for test_row in self.test_on_sample:
            self.append("sticker_print", {
                "material_specification": test_row.material_specification,
                "test_method": test_row.test_method,
                "test_description": test_row.test_description,
                "customer_specification":test_row.customer_specification,
                "sample_description":test_row.sample_description,
            })
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
            new_doc.test_description = row.test_description
            new_doc.sample_description = row.sample_description
            new_doc.child_table_id = row.name
            new_doc.document_id = row.test_id 
            new_doc.material_specification = row.material_specification
            # new_doc.remark = self.client
            new_doc.customer_specification = row.customer_specification
            new_doc.discipline = row.discipline
            new_doc.challan_no = self.challan_no
            new_doc.customer_name = self.customer

            if self.client :
                new_doc.witness = "Yes"
                new_doc.witness_name = self.client                
                
            else: 
                new_doc.witness = "No" 

                

            if row.sample_id and row.test_id:
                new_doc.document_id = f"{row.sample_id}/{row.test_id}"
            else:
                new_doc.document_id = row.test_id or row.sample_id or ""
            
            test_method_doc = frappe.get_doc("Test Method", row.test_method)
            item_doc = frappe.get_doc("Item", row.material_specification)

            for chem in test_method_doc.chemical_details:
                td = new_doc.append("test_details", {
                    "test_method": row.test_method,
                    "parameter": chem.parameter,
                    "method_min_range": chem.min_range,
                    "method_max_range": chem.max_range
                })
                for item_chem in item_doc.custom_chemical_detail:
                    if item_chem.parameter == chem.parameter:
                        td.min_range = item_chem.min_range
                        td.max_range = item_chem.max_range
            new_doc.save()

#**************************************************************************************************           
    @frappe.whitelist()        
    def get_material_sample_details(self):
        self.test_on_sample = []

        for mat_row in self.material_details:
            if mat_row.material_specification:
                item_doc = frappe.get_doc("Item", mat_row.material_specification)

                for sample_row in item_doc.custom_material_sample_details:
                    # frappe.msgprint(str(sample_row.test_method)) 
                    des_price=frappe.get_value("Test Description", sample_row.test_description, "rate")
                    test_method_doc = frappe.get_doc("Test Method", sample_row.test_method)

                    self.append("test_on_sample", {
                        "test_group": test_method_doc.test_group,
                        "test_method": sample_row.test_method,
                        "test_description": sample_row.test_description,   
                        "discipline": test_method_doc.discipline,
                        "group": sample_row.group,
                        "price":des_price,
                        "material_specification": mat_row.material_specification,
                        "material_shape": mat_row.material_shape,
                        "heat_number": mat_row.heat_number,
                        "sample_description":mat_row.sample_description,
                    })
        return self
 #***************************************************************************************   
    @frappe.whitelist()
    def update_cutting_rows(self):
        self.cutting_charge = []
        for row in self.material_details:
            if not row.material_dimension:
                continue
            dimension = float(row.material_dimension)
            material = row.material_specification 
            rows_to_add = 2 if dimension >= 50 else 0
            for i in range(rows_to_add):
                if i == 0:
                    thikdia = dimension
                else:
                    thikdia = dimension / 2
                self.append("cutting_charge", {
                    "material": material,
                    "thik_dia": thikdia
                })
        return len(self.cutting_charge)


