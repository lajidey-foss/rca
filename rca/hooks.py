from . import __version__ as app_version

app_name = "rca"
app_title = "RCApp"
app_publisher = "Jide Olayinka by Gross Innovates"
app_description = "App to help simplified returnable case workflow for liquid product with containers"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "appdev@grossin.co"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rca/css/rca.css"
# app_include_js = "/assets/rca/js/rca.js"

# include js, css files in header of web template
# web_include_css = "/assets/rca/css/rca.css"
# web_include_js = "/assets/rca/js/rca.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rca/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {"Sales Invoice" : "rcapp/api/invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

before_install = "rca.events.install.before_install"
# after_install = "rca.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rca.uninstall.before_uninstall"
# after_uninstall = "rca.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rca.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	#	
	#	"after_insert": "rca method"
	# }
	#"on_submit": "rca.rcapp.api.returnable.update_invoice"

	"Sales Invoice": {
		"on_submit": "rca.rcapp.api.returnable.update_invoice",
		"on_cancel": "rca.rcapp.api.returnable.on_main_cancel"
		
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rca.tasks.all"
# 	],
# 	"daily": [
# 		"rca.tasks.daily"
# 	],
# 	"hourly": [
# 		"rca.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rca.tasks.weekly"
# 	]
# 	"monthly": [
# 		"rca.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "rca.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rca.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rca.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"rca.auth.validate"
# ]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
                    "Sales Invoice-entry_type",
                    "Sales Invoice Item-poi_ec",
                    "Payment Entry-entry_type",
                    "Item-is_rec",
                    "Item-has_rec",
                    "Item-main_hrec_tag",
                    "Customer-is_reca",
                    "Customer-rm_party",
					"Sales Invoice-rec_for",
                ),
            ]
        ],
    },
]


