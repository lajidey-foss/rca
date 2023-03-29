# - 
# Copyright 2021 Jide Olayinka
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from erpnext.accounts.utils import get_balance_on
from frappe.utils.data import add_days, date_diff, today


#GLOBAL_MAIN_SERIES = 'MM-VCH-.YYYY.-'
#GLOBAL_RETURN_SERIES = 'RM-RET-.YYYY.-'
# work on js to restrict circular for items ec and party ec
# only item marked as returnable can be available for select
# also party can't pick itself and only customer can be available for select
GLOBAL_MAIN_ENTRY = 'MAIN VCH'
GLOBAL_RETURN_ENTRY = 'REC ENTRY'

@frappe.whitelist()
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
            rma_return_submit_invoice(doc)
        else:
            pass
    else:
        rma_main_submit_invoice (doc)

#### Direct sales
def rma_main_submit_invoice (data):
    """begin here""" 
    #print('\n\n inside main-submit \n\n')      
    vch_series = frappe.db.get_single_value('Return Material Series', 'sales_out_series')
    nqty = 0
    nsum = 0
    party_code = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)
    #print(f'\n\n main-submit party: {party_code} \n\n')

    new_item_list = get_data_sales_voucher(data)

    if(new_item_list is None ):
        return
    
    if (not len(new_item_list)> 0):
        return
   
    #print(f'\n\n Bug here len must be > 0 : {new_item_list} \n\n')
    for cal in new_item_list:
        nqty += cal['qty']
        nsum += cal['amount']
    
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.update({
        "is_pos": 0, "doc.ignore_pricing_rule" : 1, "total" : nsum, "total_qty": nqty,
        "company": data.company, "currency": data.currency ,
        "customer":party_code, "naming_series" : vch_series, 
        "set_posting_time":1, "due_date": add_days(data.posting_date, 1), "posting_date": data.posting_date,
        "update_stock":1, "set_warehouse": data.set_warehouse, "set_target_warehouse": data.set_target_warehouse,
        "items": new_item_list,"rec_for": data.name,
    })

    #cntrl_party = get_rec_party(data.customer)
    # check if empties makes credit limit to exceeded if single account 
    # party_code = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)
    if not validate_credit_limit(data, nsum):
        return
    
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.ignore_pricing_rule = 1
    invoice_doc.entry_type = GLOBAL_RETURN_ENTRY
    invoice_doc.set_missing_values()

    invoice_doc.save()
    invoice_doc.submit()

def make_rma_main (data):
    """ doc_item_record=['{}'.format(r.code) for r in data.items]
    party_record = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer) """
    

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

def rma_return_submit_invoice (data):
    """begin here"""
    vch_series = frappe.db.get_single_value('Return Material Series', 'sales_in_series')
    voucher_items = ""
    nqty, nsum = 0,0
    party_code = data.customer if validate_limit() != 'PREMIUM_PACK' else get_rec_party(data.customer)

    new_item_list = get_data_sales_voucher(data)

    if(new_item_list == None ):
        #or new_item_list == []
        return

    if (not len(new_item_list)> 0):        
        return

    for cal in new_item_list:
        nqty -= cal['qty']
        nsum -= cal['amount']
    
    # delete start

    """ for x in data.items:
        voucher_items +="\'"+ x.item_code+"\',"
    ec_list = []
    replace_ec_list = []
    item_ec_list = []
    ec_remover_list = []
    
    items_data = get_rec_items(voucher_items)
    
    if (len(items_data) <= 0):
        return

    for x in items_data:
        ec_list.append(x.main_hrec_tag)
        replace_ec_list.append({"tag":x.main_hrec_tag, "code":x.item_code, "rate":x.standard_rate})
    indexitm = 0
    for vch_item in data.items:
        if vch_item.item_code in ec_list:
            indexitm = ec_list.index(vch_item.item_code)
            ec_remover_list.append({
                "item_code": replace_ec_list[indexitm]["code"],
                "qty": vch_item.qty,
                "rate": replace_ec_list[indexitm]["rate"],
                "uom": vch_item.uom,
                "amount": vch_item.qty * replace_ec_list[indexitm]["rate"],
                "conversion_factor": vch_item.conversion_factor,
                "poi_ec":vch_item.poi_ec,
            })
        else:
            if(vch_item.poi_ec == 1):
                item_ec_list.append({
                    "item_code": vch_item.item_code,
                    "qty": vch_item.qty,
                    "rate": vch_item.rate,
                    "uom": vch_item.uom,
                    "amount": vch_item.qty * vch_item.rate,
                    "conversion_factor": vch_item.conversion_factor,
                    "poi_ec":vch_item.poi_ec,
                })

    if (len(ec_remover_list) <= 0):
        return
    """
    # use multiply (x* -1)
    # delete ends
    
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.update({
        "is_pos": 0, "doc.ignore_pricing_rule" : 1, "total" : nsum, "total_qty": nqty,
        "company": data.company, "currency": data.currency ,
        "customer":party_code, "naming_series" : vch_series, 
        "set_posting_time":1, "posting_date": data.posting_date,
        "is_return":1, "update_stock":1, "set_warehouse": data.set_warehouse, 
        "set_target_warehouse": data.set_target_warehouse, "items": new_item_list,
        "rec_for": data.name,
    })

    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.ignore_pricing_rule = 1
    invoice_doc.entry_type = GLOBAL_RETURN_ENTRY
    invoice_doc.set_missing_values()

    invoice_doc.save()
    invoice_doc.submit()
    


def get_rec_party(main_party):
    """ get list of rec party from doc"""  
    party_return = ""  
    pack = frappe.db.sql(
        """
        SELECT 
            name, 
            is_reca, 
            idx, 
            rm_party  
        FROM `tabCustomer`
        WHERE 
            disabled = 0 AND rm_party IN ('{0}')
        """.format(main_party),
        as_dict=1,
    )
    if (not len(pack) > 0):
        party_return = main_party
    else:
        party_return = pack[0]['name']  
    
    return party_return

def get_data_sales_voucher(data):
    ''' get next'''
    ec_remover_list = []
    voucher_items = ""
    doc_items = data.items
    for x in doc_items:
        voucher_items +="\'"+ x.item_code+"\',"
    
    ec_list = []
    replace_ec_list = []
    item_ec_list = []
    
    ''' get the Ec of invoice items that has Ec'''
    ec_items = get_rec_items(voucher_items)

    if(ec_items is None):
        '''just added'''
        return

    if (not len(ec_items) > 0):
        return

    for x in ec_items:
        ec_list.append(x.main_hrec_tag)
        replace_ec_list.append({"tag":x.main_hrec_tag, "code":x.item_code, "rate":x.standard_rate})
    '''modified invoice item list'''
    indexitm = 0
    for vch_item in doc_items:
        if vch_item.item_code in ec_list:
            indexitm = ec_list.index(vch_item.item_code)
            ec_remover_list.append({
                "item_code": replace_ec_list[indexitm]["code"],
                "qty": vch_item.qty,
                "rate": replace_ec_list[indexitm]["rate"],
                "uom": vch_item.uom,
                "amount": vch_item.qty * replace_ec_list[indexitm]["rate"],
                "conversion_factor": vch_item.conversion_factor,
                "poi_ec":vch_item.poi_ec,
            })
        else:
            if(vch_item.poi_ec == 1):
                item_ec_list.append({
                    "item_code": vch_item.item_code,
                    "qty": vch_item.qty,
                    "rate": vch_item.rate,
                    "uom": vch_item.uom,
                    "amount": vch_item.qty * vch_item.rate,
                    "conversion_factor": vch_item.conversion_factor,
                    "poi_ec":vch_item.poi_ec,
                })
    ###remove paid EC
    #if s is None
    if (ec_remover_list is None):
        return
        
    if (not len(ec_remover_list) > 0):
        return
    
    #adjment start here to accommadate for returns too
    for rc in item_ec_list:
        for d in ec_remover_list:
            if d['item_code'] == rc['item_code']:
                d['qty'] = d['qty'] - rc['qty']
                d['amount'] = d['qty'] * d['rate']
    
    return ec_remover_list

def get_rec_items(main_items):
    """ list of rec from voucher items list"""
    # also check if stock is maintain in item
    return frappe.db.sql(
        """ 
        SELECT
            name AS item_code,
            item_name,
            idx as idx,
            standard_rate,
            main_hrec_tag
        FROM
            `tabItem`
        WHERE
            disabled = 0
            AND is_sales_item = 1
            AND is_fixed_asset = 0
            AND is_rec = 1
            AND main_hrec_tag IN ({0})
        """.format(
            main_items[: -1]
        ),
        as_dict=1,
    )

  


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
