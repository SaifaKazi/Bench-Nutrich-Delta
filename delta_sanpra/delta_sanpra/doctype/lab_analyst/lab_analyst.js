// // Copyright (c) 2025, Sanpra Software Solution and contributors
// // For license information, please see license.txt
let items = []
frappe.ui.form.on("Lab Analyst", {
    // Form load
    onload(frm) {
        frm.page.sidebar.hide();
        let original_print = frm.print_doc || frm.print_preview;

        frm.print_doc = function () {
            frm.set_value("is_print", 1);
            frm.save_or_update();
            original_print.call(frm);
        };


    },
    refresh(frm) {
        apply_highlight_from_backend(frm);

        frm.set_query("parameter", "test_details", function () {
            return {
                filters: [
                    ["Chemical Parameter", "name", "in", items]
                ]
            }
        })
    },
    // after_save(frm) {
    //     apply_highlight_from_backend(frm);
    // },
    // onload_post_render(frm) {
    //     apply_highlight_from_backend(frm);
    // },
    // ****************************************************************************************8
    // async upload_excel_file(frm) {
    //     if (frm.doc.upload_excel_file) {
    //         await frm.call({
    //             method: "create_rate_chart_from_excel",
    //             doc: frm.doc,
    //         });
    //         frm.refresh_field("test_details");
    //         apply_highlight_from_backend(frm);
    //     }
    // },
    upload_excel_file(frm) {
        if (frm.doc.upload_excel_file) {
            frm.call({
                method: "create_rate_chart_from_excel",   // Calls Python method
                doc: frm.doc,
            }).then(() => {
                frm.refresh_field("test_details");       // Refresh child table
                apply_highlight_from_backend(frm);       // Custom handler
            });
        }
    }
});
// *****************************************************************************************************
frappe.ui.form.on("Test Details", {
    value(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.value && row.method_min_range && row.method_max_range) {
            let val = parseFloat(row.value);
            let min = parseFloat(row.method_min_range);
            let max = parseFloat(row.method_max_range);
            let status = (val < min || val > max) ? "NON NABL" : "NABL";
            frappe.model.set_value(cdt, cdn, "status", status);
        }
        apply_highlight_from_backend(frm);
    },
    //*************************************************************
    test_method(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "parameter", "");

        items = []
        frappe.call({
            method: "get_test_method",
            doc: frm.doc,
            args: { test_method: child.test_method },
            callback: function (r) {
                console.log(r)
                if (r.message && r.message.length > 0) {
                    // items.push(r.message)
                    r.message.forEach(row => {
                        items.push(row)
                    });
                    frm.refresh_field("test_details");
                }
            }
        });
    },
    parameter(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        frappe.call({
            method: "get_minmax_range",
            doc: frm.doc,
            args: { test_method: child.test_method, parameter: child.parameter, material_specification: frm.doc.material_specification },
            callback: function (r) {
                console.log(r)
                if (r.message && r.message.length > 0) {
                    let data = r.message[0];
                    frappe.model.set_value(cdt, cdn, "method_min_range", data.method_min_range || "");
                    frappe.model.set_value(cdt, cdn, "method_max_range", data.method_max_range || "");
                    frappe.model.set_value(cdt, cdn, "min_range", data.min_range || "");
                    frappe.model.set_value(cdt, cdn, "max_range", data.max_range || "");
                    if (child.value) {
                        let val = parseFloat(child.value);
                        let min = parseFloat(data.method_min_range);
                        let max = parseFloat(data.method_max_range);

                        let status = (val < min || val > max) ? "NON NABL" : "NABL";
                        frappe.model.set_value(cdt, cdn, "status", status);
                    }
                    frm.refresh_field("test_details");
                }
            }
        });
    },
});
function apply_highlight_from_backend(frm) {
    if (!frm || !frm.docname) return;

    frm.call({
        method: "get_highlight_colors",
        doc: frm.doc,
        callback: function (r) {
            if (!r.message) return;
            const colors = r.message;

            // ✅ Apply for both tables
            const tables = ["test_details", "test_details_physical"];

            tables.forEach(table => {
                const grid_field = frm.fields_dict[table];
                if (!grid_field || !grid_field.grid) return;
                const grid = grid_field.grid;

                grid.grid_rows.forEach(row => {
                    const cell = $(row.columns["value"]);
                    const input = cell.find("input");
                    const color = colors[row.doc.name] || "";

                    if (input.length) {
                        input.css({
                            "background-color": color,
                            "transition": "background-color 0.2s ease"
                        });
                    } else {
                        cell.css({
                            "background-color": color,
                            "transition": "background-color 0.2s ease"
                        });
                    }
                });
            });
        }
    });
}

//******************************************************************************************************