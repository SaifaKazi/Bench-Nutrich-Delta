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
        // frm.set_query("test_description","custom_material_sample_details", function() {
        //     return {
        //         filters: [
        //             ["Test Description","name","in",description]
        //         ]   
        //     }  
        // })
    }, 
    custom_standard: set_item_name,
    custom_year: set_item_name,
    custom_grade: set_item_name  
});
function set_item_name(frm) {
    let standard = frm.doc.custom_standard || "";
    let year = frm.doc.custom_year || "";
    let grade = frm.doc.custom_grade || "";

    if (standard && year && grade) {
        frm.set_value("item_name", `${standard} : ${year} ${grade}`);
    } else if (standard && year) {
        frm.set_value("item_name", `${standard} : ${year}`);
    } else if (standard && grade) {
        frm.set_value("item_name", `${standard} : ${grade}`);
    } else if (standard) {
        frm.set_value("item_name", standard);
    } else {
        frm.set_value("item_name", "");
    }
}


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

