frappe.ui.form.on("Sales Invoice", {
    
    is_return(frm){
		if(frm.doc.is_return){
			cur_frm.set_value("entry_type", " ");	
		}
	},
	refresh(frm){
		//console.table(frm.doc);
		if(frm.doc.return_against != null && frm.doc.is_return && frm.doc.name == 'new-sales-invoice-1' ){
			//console.log('return against in refresh -- got here: '+ frm.doc.docstatus);
			cur_frm.set_value("entry_type", " ");	
		}
	},
})