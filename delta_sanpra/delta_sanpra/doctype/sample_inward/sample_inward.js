// Copyright (c) 2025, Sanpra Software Solution and contributors
// For license information, please see license.txt

let items = []
let item1 = []
let description = []
frappe.ui.form.on("Sample Inward", {
	date(frm) {
		if (frm.doc.challan_date > frm.doc.date) {
			frappe.msgprint("Challan Date cannot be greater than date");
		}
	
	},
	challan_date(frm) {
		if (frm.doc.challan_date > frm.doc.date) {
			frappe.msgprint("Challan Date cannot be greater than date");
		}
	
	},
 
	quantity(frm) {
        if (!frm.doc.quantity) return;

        frm.call({
            method: "update_material_rows",
            doc: frm.doc,
            freeze: true,
            freeze_message: __("Updating rows..."),
            callback: function() {
                frm.refresh_field("material_details");
            }
        });
    },
   refresh: function(frm) {
        frm.set_query("material_specification","test_on_sample", function() {
            return {
                filters: [
                    ["Item","name","in",items]
                ]   
            }  
        })
        frm.set_query("test_method","test_on_sample",function(){
            return{
                filters:[
                    ["Test Method","name","in",item1]
                ]
            }
        })
        frm.set_query("test_description","test_on_sample", function() {
            return {
                filters: [
                    ["Test Description","name","in",description]
                ]   
            }  
        })
    },
    onload(frm) {
        frm.page.sidebar.hide();  
        frm.doc.material_details.forEach(row => {
                if (row.material_specification) {
                    items.push(row.material_specification);
                }
            })
        },
    get_sample(frm){
        frappe.call({
            method: "get_material_sample_details",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_field("test_on_sample");
                // frm.reload_doc(); 
            }
        });
    }
    
});

frappe.ui.form.on("Material Details", {
    material_specification(frm, cdt, cdn) {
        update_items_array(frm);
    },
    material_details_remove(frm, cdt, cdn) {
        update_items_array(frm);
    },
    onload(frm) {
        update_items_array(frm);
    },
    material_details_remove(frm, cdt, cdn) {
        update_items_array(frm);
        call_get_material_dimension(frm);
    },
    material_dimension(frm, cdt, cdn) {
        call_cutting_row_update(frm);
    },
    material_specification(frm, cdt, cdn) {
        call_cutting_row_update(frm);
    },
    material_details_add: function (frm, cdt, cdn) {
        let qty = frm.doc.quantity || 0; 
        let rows = frm.doc.material_details.length;
        if (rows > qty) {
            frappe.msgprint(
                __("You cannot add more than {0} Material Details rows because Quantity is {0}", [qty])
            );
            frm.doc.material_details.pop();
            frm.refresh_field("material_details");
            return false;
        }
    }
});

function update_items_array(frm) {
    items = []; // clear first
    (frm.doc.material_details || []).forEach(row => {
        if (row.material_specification) {
            items.push(row.material_specification);
        }
    });
    console.log("Updated items:", items);
} 
function call_cutting_row_update(frm) {
    frm.call({
        method: "update_cutting_rows",
        doc: frm.doc,
        freeze: true,
        freeze_message: __("Updating cutting charge rows..."),
        callback: function () {
            frm.refresh_field("cutting_charge");
        }
    });
}

frappe.ui.form.on("Test On sample", {
    test_group(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "test_method", "");

        if (!child.test_group) {
            return;
        }

        item1 = [];

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Test Method",
                filters: { test_group: child.test_group },
                fields: ["name"]
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    r.message.forEach(row => {
                        item1.push(row.name);
                    });
                    frappe.meta.get_docfield("Test On Sample", "test_method", frm.doc.name).options = item1;
                    frm.refresh_field("test_on_sample");
                }
            }
        });
    },
    test_method(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "test_description", "");

        if (!child.test_method) {
            return;
        }
        description = [];

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Test Description",
                filters: { test_method: child.test_method },
                fields: ["name"]
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    r.message.forEach(row => {
                        description.push(row.name);
                    });
                    frappe.meta.get_docfield("Test On Sample", "test_description", frm.doc.name).options = description;
                    frm.refresh_field("test_on_sample");
                }
            }
        });
    },
    test_description: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];

        if (child.test_description) {
            frappe.db.get_value("Test Description", child.test_description, "rate", (r) => {
                if (r && r.rate) {
                    frappe.model.set_value(cdt, cdn, "price", r.rate);
                } else {
                    frappe.model.set_value(cdt, cdn, "price", 0);
                }
            });
        } 
        else {
            frappe.model.set_value(cdt, cdn, "price", 0);
        }
    }
});



