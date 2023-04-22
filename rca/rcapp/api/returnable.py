# - 
# Copyright 2021 Jide Olayinka
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from erpnext.accounts.utils import get_balance_on
from frappe.utils.data import add_days, date_diff, today


# work on js to restrict circular for items ec and party ec
# only item marked as returnable can be available for select
# also party can't pick itself and only customer can be available for select
GLOBAL_MAIN_ENTRY = 'MAIN VCH'
GLOBAL_RETURN_ENTRY = 'REC ENTRY'


def update_invoice(doc, method):
    
    if not frappe.db.get_single_value('Material Return Settings', 'auto_rec_posting'):
        return
    

    if(doc.entry_type == GLOBAL_RETURN_ENTRY ):
        # it is auto generated invoice by this app therefore trap it
        return

    if(doc.is_return):
        if validate_limit() == 'FREEMIUM_PACK' :
            pass
        elif validate_limit() == 'PREMIUM_PACK' :
            #rma_return_submit_invoice(doc)
            make_rma_return(doc)
        else:
            pass
    else:
        make_rma_main(doc)

def make_rma_main (data):
    """ vch_series =  {{abr}}-RET-.YYYY.-"""
    coy = frappe.get_doc('Company', data.company)
    vch_series = coy.abbr+'-'+frappe.db.get_single_value('Return Material Series', 'sales_out_series')
    doc_item_record= get_doc_items(data)
    party_record = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)

    total_qty,total_amount = 0.0,0.0

    if(doc_item_record is None  or doc_item_record == []):
        return

    for ntotal in doc_item_record:
        total_qty += ntotal['qty']
        total_amount += ntotal['amount']
    
    si_doc = frappe.new_doc("Sales Invoice")
    si_doc.update({
        "is_pos": 0, "company": data.company, "currency": data.currency ,
        "customer":party_record, "naming_series" : vch_series, 
        "set_posting_time":1, "due_date": add_days(data.posting_date, 1), "posting_date": data.posting_date,
        "update_stock":data.update_stock, "set_warehouse": data.set_warehouse, "set_target_warehouse": data.set_target_warehouse,
        "items": doc_item_record,"rec_for": data.name,"entry_type" :GLOBAL_RETURN_ENTRY
    })

    if not validate_credit_limit(data, total_amount):
        return
    
    si_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    si_doc.set_missing_values()

    si_doc.save()
    si_doc.submit()
    

def validate_limit ():
  """ work on to get limit """
  with open(frappe.get_site_path('rec_app.json')) as jsonfile:
      parsed = json.load(jsonfile)
  valid_period = parsed["rec_valid_till"]
  module_status = parsed["rca_status"]
  diff = date_diff(valid_period, today())
  if module_status == 'premium' :
      return 'PREMIUM_PACK'

  elif not module_status == 'freemium' and diff > 0 :
      return 'PREMIUM_PACK'
  elif not module_status == 'freemium' and diff < 0 :
      return 'FREEMIUM_PACK'
  else:
    return 'FREEMIUM_PACK'


def make_rma_return (data):
    """"""   
    coy = frappe.get_doc('Company', data.company)
    vch_series = coy.abbr+'-'+frappe.db.get_single_value('Return Material Series', 'sales_in_series')
    doc_item_record= get_doc_items(data)
    party_record = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)
        

    if(doc_item_record is None  or doc_item_record == []):
        return
    
    total_qty,total_amount = 0.0,0.0

    for ntotal in doc_item_record:
        total_qty -= ntotal['qty']
        total_amount -= ntotal['amount']
    
    si_doc = frappe.new_doc("Sales Invoice")
    si_doc.update({
        "is_pos": 0, "company": data.company, "currency": data.currency ,
        "customer":party_record, "naming_series" : vch_series, 
        "set_posting_time":1, "posting_date": data.posting_date,
        "update_stock":data.update_stock, "set_warehouse": data.set_warehouse, 
        "set_target_warehouse": data.set_target_warehouse, "is_return":1,
        "items": doc_item_record,"rec_for": data.name,"entry_type" :GLOBAL_RETURN_ENTRY
    })
    
    si_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    si_doc.set_missing_values()

    si_doc.save()
    si_doc.submit()



def get_rec_party(main_party):
    """ get list of rec party from doc"""  
    party_return = ""  
    
    party_rm_checker = frappe.db.get_list("Customer", fields="name,is_reca,rm_party", filters={
        "disabled": 0,"rm_party": ["in", main_party]
    })
   
    if (party_rm_checker is None or party_rm_checker == []):
        party_return = main_party
    else:
        party_return = party_rm_checker[0]['name']  
    
    return party_return


def get_doc_items(data):
    """"""
    voucher_items_record=['{}'.format(r.item_code) for r in data.items]

    link_to_items  =  get_rec_item(voucher_items_record)
        
    if(link_to_items is None  or link_to_items == []):
        return

    set_items_row = []
    poi_ec_list=[]

    for rcord in data.items:
        for itm in link_to_items:  
            if rcord.item_code == itm.main_hrec_tag:
                set_items_row.append({
                    "item_code": itm.name,
                    "qty": rcord.qty,
                    "rate": itm.standard_rate,
                    "uom": rcord.uom,
                    "amount": rcord.qty * itm.standard_rate,
                    "conversion_factor": rcord.conversion_factor,
                    "poi_ec":rcord.poi_ec,
                })
                
            else:
                if (rcord.item_code == itm.name):
                    poi_ec_list.append({
                        "item_code": itm.name,
                        "qty": rcord.qty,
                        "rate": itm.standard_rate,
                        "uom": rcord.uom,
                        "amount": rcord.qty * itm.standard_rate,
                        "conversion_factor": rcord.conversion_factor,
                        "poi_ec":rcord.poi_ec,
                    })
                    
                if(rcord.poi_ec == 1):
                    print(f'\n === poi_ec : 1 === \n')
                    """ poi_ec_list.append({
                        "item_code": rcord.item_code,
                        "qty": rcord.qty,
                        "rate": rcord.rate,
                        "uom": rcord.uom,
                        "amount": rcord.qty * rcord.rate,
                        "conversion_factor": rcord.conversion_factor,
                        "poi_ec":rcord.poi_ec,
                    }) """
                    #print('*********************************************')
                #print(f'\n poi : {poi_ec_list} \n')

    if(set_items_row is None  or set_items_row == []):
        return
    
    # sort out paid on doc returnable case
    if(not poi_ec_list is None):
        for pl in poi_ec_list:
            for dr in set_items_row:
                if dr['item_code'] == pl['item_code']:
                    if pl["qty"] > dr["qty"] :
                        msg = f"<div>Warning, Quantity for RM: {dr['item_code']} exceeding by {pl['qty'] - dr['qty']} </div>"        
                        frappe.throw(_(msg))
                    zero_qty_checker = dr['qty'] - pl['qty']
                    if zero_qty_checker == 0 :
                        set_items_row.remove(dr)
                    else:
                        dr['qty'] = zero_qty_checker
                        
            
    return set_items_row

def get_rec_item(main_item):
    """"""
    rc_item = frappe.db.get_list("Item", fields="name,item_name,standard_rate,main_hrec_tag", filters={
        "disabled": 0,"is_sales_item": 1,"is_fixed_asset": 0,"is_rec": 1,"main_hrec_tag": ["in", main_item]
    })
    return rc_item

    

def validate_credit_limit (data, ec_nsum):
    '''validate_credit_limit (data, ec_sum)
    if not single account get the corresponding acc 
    party_code = get_rec_party(data.customer)
    then it get bal and credit limit
    '''
    #party_code = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)
    if not validate_limit() == 'PREMIUM_PACK' :
        return True
    

    cntrl_party = get_rec_party(data.customer)
    if not data.customer == cntrl_party :
        return True
    
    ctrl_find_limit = frappe.db.sql(
        """
        SELECT parent, credit_limit, company
        FROM `tabCustomer Credit Limit`
        WHERE parent= '{0}' AND company= '{1}' AND docstatus=0 AND parentfield='credit_limits' AND parenttype='Customer'
        """.format(cntrl_party,data.company), as_dict=1,
    )
    #(len(ec_remover_list) <= 0)
    #if (ec_remover_list is None):
    if(ctrl_find_limit is None):
        return True
        
    if(not len(ctrl_find_limit) > 0 )  :
        #print(f'\n\n\n\n inside valid : {len(ctrl_find_limit)} \n\n\n\n')
        return True
    
    
    if(not (ctrl_find_limit[0]['credit_limit']) > 0):
        #print(f"\n\n\n\n inside validate : {ctrl_find_limit[0]['credit_limit']} \n\n\n\n")
        return True
    
    contr_party_bal = get_balance_on(
        date = data.posting_date,
        party_type = 'Customer',
        party = cntrl_party
    )
        
    ctrl_allsum = contr_party_bal+ data.total + ec_nsum
    if (ctrl_allsum > ctrl_find_limit[0]['credit_limit']):
        msg = f"<div>Warning, case exceeding the credit limit allowed {(ctrl_allsum - ctrl_find_limit[0]['credit_limit'])} </div>"        
        frappe.throw(_(msg))
    
    return True

def on_main_cancel(doc, method):
    
    frappe.db.set_value('Sales Invoice',{"rec_for":doc.name},'docstatus',2)