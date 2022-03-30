# Copyright (c) 2022, Jide Olayinka by Gross Innovates and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, date_diff, flt, getdate

def execute(filters=None):
	#filter here
	columns, data = [], []
	conditions, condition_type="",""
	
	if filters.from_date and filters.to_date:
		if filters.from_date==None:
			filters.from_date = frappe.datetime.get_today()
			#print('\n\n\n\n from time is: {filters.from_date} \n\n\n\n')
		if filters.to_date==None:
			filters.to_date = frappe.datetime.get_today()
			#print('\n\n\n\n to time is: {filters.to_date} \n\n\n\n')
	conditions = "AND posting_date BETWEEN '"+ filters.from_date+"' AND '" + filters.to_date+"'"

	if filters.get("party"):
		c_party = filters.get("party")
		conditions += f"AND party='{c_party}'"
		#AND party='Tosin VSM'
	
	if filters.get("entry_type"):
		e_type = filters.get("entry_type")
		condition_type = f"AND entry_type='{e_type}'"

	#columns here
	columns = [
		{'fieldname':'voucher_no','label':'Invoice No','width':'180'},
		{'fieldname':'posting_date','label':'Invoice Date','width':'80'},
		{'fieldname':'party','label':'Customer','width':'150'},
		{'fieldname':'debit','label':'Debit','width':'120'},
		{'fieldname':'credit','label':'Credit','width':'120'},
		{'fieldname':'voucher_type','label':'voucher type','width':'100'},
		{'fieldname':'entry_type','label':'entry type','width':'100'}
	]

	#query here
	#print('\n\n\n\n to time is: {filters.to_date} \n\n\n\n')
	#print('\n\n\n\n from time is: {filters.from_date} \n\n\n\n')
	data_befor = frappe.db.sql(
		"""
		SELECT * FROM (
		SELECT  voucher_no, posting_date, party, debit, credit, voucher_type, docstatus,
		CASE WHEN voucher_type ='Sales Invoice' THEN (SELECT entry_type FROM `tabSales Invoice` WHERE name=voucher_no ) 
		WHEN voucher_type ='Payment Entry' THEN (SELECT entry_type FROM `tabPayment Entry` WHERE name=voucher_no ) ELSE 'pend' END AS entry_type
		FROM `tabGL Entry` 
		WHERE party_type='Customer' {} ) a WHERE docstatus = 1 {}
		""".format( conditions, condition_type),as_dict=1,
	)
	
	data = data_befor
	return columns, data

