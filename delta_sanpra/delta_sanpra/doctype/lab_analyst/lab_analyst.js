// // Copyright (c) 2025, Sanpra Software Solution and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Lab Analyst", {
    onload(frm) {
        frm.page.sidebar.hide();  
        let original_print = frm.print_doc || frm.print_preview;

        frm.print_doc = function() {
            frm.set_value("is_print", 1);
            frm.save_or_update();
            original_print.call(frm);
        };
    },
    async upload_excel_file(frm) {
        if (frm.doc.upload_excel_file) {
            await frm.call({
                method: "create_rate_chart_from_file",
                doc: frm.doc,
                freeze: true,
                freeze_message: "Importing test details...",
            });
            frm.reload_doc();
        }
    }
});
