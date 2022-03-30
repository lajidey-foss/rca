// Copyright (c) 2022, Jide Olayinka by Gross Innovates and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Return Settings', {
	onload_post_render: function (frm){
		frm.disable_save();
		frm.call('get_info').then( r => {
			frm.refresh();
		})
	}

});
