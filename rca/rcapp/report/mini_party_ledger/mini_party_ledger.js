// Copyright (c) 2022, Jide Olayinka by Gross Innovates and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Mini Party Ledger"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -5),
			"reqd": 1,
			"width": "35px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "35px"
		},		
		{
			"fieldname":"entry_type",
			"label": __("Entry Type"),
			"fieldtype": "Select",
			"options": "\nMAIN VCH\nREC ENTRY",
			"default": ""
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "",
			"hidden": 1,
			on_change: function() {
				frappe.query_report.set_filter_value('party', "");
			}
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Link",
			"options": "Customer",
			/*
			get_data: function(txt) {
				if (!frappe.query_report.filters) return;

				return frappe.db.get_link_options('Customer', txt);
			},
			
			on_change: function() {
				var party_type = frappe.query_report.get_filter_value('Customer');
				var parties = frappe.query_report.get_filter_value('party');

				if(!party_type || parties.length === 0 || parties.length > 1) {
					frappe.query_report.set_filter_value('party_name', "");
					frappe.query_report.set_filter_value('tax_id', "");
					return;
				}
				var party = parties[0];
				var fieldname = erpnext.utils.get_party_name(party_type) || "name";
				frappe.db.get_value(party_type, party, fieldname, function(value) {
					frappe.query_report.set_filter_value('party_name', value[fieldname]);
				});

				if (party_type === "Customer" || party_type === "Supplier") {
					frappe.db.get_value(party_type, party, "tax_id", function(value) {
						frappe.query_report.set_filter_value('tax_id', value["tax_id"]);
					});
				}
			}*/
		},
		{
			"fieldname":"party_name",
			"label": __("Party Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "debit" && data && data.debit > 0) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "credit" && data && data.credit > 0) {
			value = "<span style='color:green; font-weight:bolder'>" + value + "</span>";
		}

		return value;
	}
	
};

/* frappe.ui.form.on('Mini Party Ledger', {
	after_datatable_render: table_instance => {


		table_instance.style.setStyle(`.dt-cell__content--col-4`,{backgroundColor:'#00ff00'});
		table_instance.style.setStyle(`.dt-cell__content--col-5`).addClass("text-danger");;
	}
}) */