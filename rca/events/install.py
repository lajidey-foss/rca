import frappe
import json
from frappe.utils import data
from frappe.utils.data import add_days, today
from uuid import uuid4
#import os

def before_install():
    ''' hold here'''
    trials =  add_days(today(), 30) 
    unique_id = str(uuid4())

    data = {
        'cuid': unique_id,
        'trial_ends': trials,
        'rca_status': 'freemium',
        'rec_valid_till': trials
    }

    with open(frappe.get_site_path('rec_app.json'), 'w') as outfile:
        json.dump(data, outfile, indent=2)
    
    file_path = frappe.utils.get_bench_path() + '/' + \
        frappe.utils.get_site_name(frappe.local.site) + \
            '/rec_app.json'
    
    print ('\n file rec_app.json created at', file_path, 'with the following settings:')
    for key in data : print("\t {}: {}".format(key, data[key]))
    print('\n Change the values in rec_app.json to effects limits \n')
