# Copyright (c) 2022, Jide Olayinka by Gross Innovates and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import cint, date_diff, flt, getdate
from erpnext import get_company_currency, get_default_company

def execute(filters=None):
	#filter here
	columns, data = [], []
	conditions, condition_type="",""

	if filters.get("company"):
		currency = get_company_currency(filters["company"])
	else:
		company = get_default_company()
		currency = get_company_currency(company)

	
	if filters.from_date and filters.to_date:
		if filters.from_date==None:
			filters.from_date = frappe.datetime.get_today()
			#print('\n\n\n\n from time is: {filters.from_date} \n\n\n\n')
		if filters.to_date==None:
			filters.to_date = frappe.datetime.get_today()
			#print(f'\n\n\n\n to time is: {filters.to_date} \n\n\n\n')
	conditions = "AND posting_date BETWEEN '"+ filters.from_date+"' AND '" + filters.to_date+"'"

	if filters.get("party"):
		c_party = filters.get("party")
		conditions += f"AND party='{c_party}'"
	
	if filters.get("entry_type"):
		e_type = filters.get("entry_type")
		condition_type = f"AND entry_type='{e_type}'"

	#columns here
	columns = [
		{'fieldname':'voucher_no','label':'Invoice No',"fieldtype": "Dynamic Link",'width':200,},
		{'fieldname':'posting_date','label':'Invoice Date','width':110},
		{'fieldname':'party','label':'Customer','width':200},
		{'fieldname':'debit','label':_("Debit "),"fieldtype": "Currency", "width": 130, "options": "currency"},
		{'fieldname':'credit','label':_("Credit "),"fieldtype": "Currency", "width": 130, "options": "currency"},
		{'fieldname':'voucher_type','label':'voucher type','width':110},
		{'fieldname':'entry_type','label':'entry type','width':100}
	]

	#query here
	data_befor = frappe.db.sql(
		"""		
		SELECT voucher_no,posting_date,party,debit,credit,voucher_type,entry_type,g_docstatus FROM (
		SELECT voucher_no, posting_date, party, debit, credit, voucher_type,party_type,
		CASE WHEN voucher_type ='Sales Invoice' THEN (SELECT entry_type FROM `tabSales Invoice` WHERE name=voucher_no ) 
		WHEN voucher_type ='Payment Entry' THEN (SELECT entry_type FROM `tabPayment Entry` WHERE name=voucher_no ) ELSE 'MAIN JVR' END AS entry_type,
		CASE WHEN voucher_type ='Sales Invoice' THEN (SELECT docstatus FROM `tabSales Invoice` WHERE name=voucher_no ) 
		WHEN voucher_type ='Payment Entry' THEN (SELECT docstatus FROM `tabPayment Entry` WHERE name=voucher_no ) ELSE 3 END AS g_docstatus
		FROM `tabGL Entry` 
		) G WHERE g_docstatus = 1 AND party_type='Customer' {0} {1}
		""".format( conditions, condition_type),as_dict=1,
	)
	
	data = data_befor
	return columns, data

