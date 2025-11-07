let test = []
description =[]
frappe.ui.form.on("Item", {
    onload(frm) {
        frm.page.sidebar.hide();     
    },  
    refresh(frm){
        frm.set_query("test_method","custom_material_sample_details",function(){
            return{
                filters:[
                    ["Test Method","name","in",test]
                ]
            }
        })
        frm.set_query("test_description","custom_material_sample_details", function() {
            return {
                filters: [
                    ["Test Description","name","in",description]
                ]   
            }  
        })
    }  
}); 

frappe.ui.form.on("Material Sample Details", {
    test_group(frm, cdt, cdn) {
        let child = locals[cdt][cdn]; 

        test = []; 

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
                        test.push(row.name);
                    });
 
                }
            }
        });
    },
    test_method(frm, cdt, cdn) {
        let child = locals[cdt][cdn];

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

                }
            }
        });
    }

});