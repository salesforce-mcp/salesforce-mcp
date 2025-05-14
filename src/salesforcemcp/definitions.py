import mcp.types as types

createObjectSchema ={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the object to be created. Fill always a value",
        },
        "plural_name": {
            "type": "string",
            "description": "The plural name of the object to be created. Fill always a value",
        },
        "description": {
            "type": "string",
            "description": "The general description of the object purpose in a short sentence. Fill always a value",
        },
        "api_name": {
            "type": "string",
            "description": "The api name of the object to be created finished with __c",
        },
        "fields": {
            "type": "array",
            "description": "The fields of the object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Text", "Number", "Lookup", "LongText", "Picklist", "Checkbox"],
                    "default": "Text",
                    "description": "The type of the field",
                 },
                "label": {
                    "type": "string",
                    "description": "The display name of the field",
                 },
                "api_name": {
                    "type": "string",
                    "description": "The api_name of the field finished in __c",
                 },
                "picklist_values": {
                    "type": "array",
                    "description": "The values of the field when the type is picklist",
                    "items": {"type": "string"},
                }
            },
            "additionalProperties": True,
        },
    },
    "required": ["name" "plural_name", "api_name", "description", "fields"],
}

createFieldSchema = createObjectSchema

def get_tools():
    tools = [
        types.Tool(
            name="create_object",
            description="Create a new object in salesforce",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the object to be created",
                    },
                    "plural_name": {
                        "type": "string",
                        "description": "The plural name of the object to be created",
                    },
                    "description": {
                        "type": "string",
                        "description": "The general description of the object purpose in a short sentence",
                    },
                    "api_name": {
                        "type": "string",
                        "description": "The api name of the object to be created finished with __c",
                    },
                },
                "required": ["name" "plural_name", "api_name"], 
            },
        ),
        types.Tool(
            name="create_object_with_fields",
            description="Create a new object in salesforce",
            inputSchema=createObjectSchema,
        ),
        types.Tool(
            name="create_custom_field",
            description="Add one or more fields in the specified custom object",
            inputSchema=createFieldSchema,
        ),
        types.Tool(
            name="delete_object_fields",
            description="Delete fields in a salesforce custom object",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_name": {
                        "type": "string",
                        "description": "The api name of the object where the fields should be deleted",
                    },
                    "fields": {
                        "type": "array",
                        "description": "The fields of the object to be deleted",
                        "properties": {
                            "api_name": {
                                "type": "string",
                                "description": "The api_name of the field finished in __c",
                             },
                        },
                    },
                },
                "required": ["api_name", "fields"],
            },
        ),
        types.Tool(
            name="create_tab",
            description="Creates a new Custom Tab in Salesforce (for Custom Objects, VF Pages, or Web Links).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tab_api_name": {
                        "type": "string",
                        "description": "The unique API name for the Tab itself. For Custom Object tabs, this MUST match the object's API name (e.g., MyCustomObject__c). For other types, choose a unique API name (e.g., My_VF_Page_Tab).",
                    },
                    "label": {
                        "type": "string",
                        "description": "The display label for the tab shown to users.",
                    },
                    "motif": {
                        "type": "string",
                        "description": "REQUIRED: The icon style (e.g., 'Custom1: Umbrella', 'Custom57: Account'). MUST follow the 'Custom<Number>: <Name>' format with a colon and space. Do NOT use underscores (e.g., 'Custom1_Umbrella' is INVALID). Find valid motifs in Salesforce Setup > User Interface > Tabs.",
                    },
                    "tab_type": {
                        "type": "string",
                        "description": "The type of tab to create.",
                        "enum": ["CustomObject", "VisualforcePage", "Web"],
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Required only if tab_type is 'CustomObject'. Must match tab_api_name.",
                    },
                    "vf_page_name": {
                        "type": "string",
                        "description": "Required only if tab_type is 'VisualforcePage'. The API name of the Visualforce page.",
                    },
                    "web_url": {
                        "type": "string",
                        "description": "Required only if tab_type is 'Web'. The URL the tab should link to.",
                    },
                     "url_encoding_key": {
                        "type": "string",
                        "description": "Optional for tab_type 'Web'. Defaults to UTF8.",
                        "enum": ["UTF8", "ISO-8859-1"],
                        "default": "UTF8",
                    },
                    "description": {
                        "type": "string",
                        "description": "An optional description for the tab.",
                    },
                },
                "required": ["tab_api_name", "label", "motif", "tab_type"],
            },
        ),
        types.Tool(
            name="create_custom_app",
            description="Creates a new Lightning Custom Application.",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_name": {
                        "type": "string",
                        "description": "The API name for the custom application (e.g., My_Warehouse_App). Should not contain spaces or special characters other than underscore."
                    },
                    "label": {
                        "type": "string",
                        "description": "The display label for the application shown to users."
                    },
                    "nav_type": {
                        "type": "string",
                        "description": "Navigation type for the app.",
                        "enum": ["Standard", "Console"],
                        "default": "Standard"
                    },
                    "tabs": {
                        "type": "array",
                        "description": "List of API names for the tabs to include (e.g., ['standard-Account', 'MyObject__c', 'My_VF_Tab']).",
                        "items": { "type": "string" }
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the application."
                    },
                    "header_color": {
                        "type": "string",
                        "description": "Optional header color in hex format (e.g., #FF0000)."
                    },
                    "form_factors": {
                        "type": "array",
                        "description": "List of form factors the app supports.",
                        "items": {"type": "string", "enum": ["Small", "Large"]},
                        "default": ["Small", "Large"]
                    },
                    "setup_experience": {
                        "type": "string",
                        "description": "The Setup Experience perspective.",
                        "enum": ["all", "sales", "service", "platform", "marketing"], # Add others as needed
                        "default": "all"
                    }
                },
                "required": ["api_name", "label", "tabs"]
            },
        ),
        types.Tool(
            name="create_report_folder",
            description="Creates a new Report Folder in Salesforce via the Metadata API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_api_name": {"type": "string", "description": "The API name of the report folder to create (no spaces).", "pattern": "^[A-Za-z0-9_]+$", "examples": ["My_Reports"]},
                    "folder_label": {"type": "string", "description": "The display label for the report folder.", "examples": ["My Reports"]},
                    "access_type": {"type": "string", "description": "The access type for the folder. Use 'Public' or 'Private'.", "enum": ["Public","Private"], "default": "Private"}
                },
                "required": ["folder_api_name","folder_label"]
            }
        ),
        types.Tool(
            name="create_dashboard_folder",
            description="Creates a new Dashboard Folder in Salesforce via the REST API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_api_name": {"type": "string", "description": "The API name of the dashboard folder to create (no spaces).", "pattern": "^[A-Za-z0-9_]+$", "examples": ["My_Dashboards"]},
                    "folder_label": {"type": "string", "description": "The display label for the dashboard folder.", "examples": ["My Dashboards"]},
                    "access_type": {"type": "string", "description": "The access type for the folder. Use 'Public' or 'Private'.", "enum": ["Public","Private"], "default": "Private"}
                },
                "required": ["folder_api_name","folder_label"]
            }
        ),
        types.Tool(
            name="create_validation_rule",
            description="Creates a new Validation Rule on a specific object via the Tooling API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "API name of the object to add the rule to (e.g., 'Account')."},
                    "rule_name": {"type": "string", "description": "Developer name for the validation rule (no .report or folder).", "pattern": "^[A-Za-z][A-Za-z0-9_]*$"},
                    "active": {"type": "boolean", "description": "Whether the rule is active.", "default": True},
                    "description": {"type": "string", "description": "Longer description of the rule (optional)."},
                    "error_condition_formula": {"type": "string", "description": "Formula that triggers the rule when true."},
                    "error_message": {"type": "string", "description": "Error message shown when rule fires.", "maxLength": 255},
                    "error_display_field": {"type": "string", "description": "Field to display the error on (optional)."}
                },
                "required": ["object_name", "rule_name", "error_condition_formula", "error_message"]
            }
        ),
        # --- Data Operations ---
        types.Tool(
            name="run_soql_query",
            description="Executes a SOQL query against Salesforce.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SOQL query to execute (e.g., SELECT Id, Name FROM ObjectName LIMIT 10).",
                        "examples": [
                            "SELECT Id, Name FROM Account LIMIT 10",
                            "SELECT Name, Amount FROM Opportunity WHERE CloseDate = THIS_YEAR ORDER BY Amount DESC NULLS LAST",
                            "SELECT Subject, Status, Priority FROM Case WHERE IsClosed = false",
                            "SELECT COUNT(Id) FROM Contact WHERE AccountId = '001...' "
                        ]
                    },
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="run_sosl_search",
            description="Executes a SOSL search against Salesforce.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "The SOSL search string (e.g., 'FIND {MyCompany} IN ALL FIELDS RETURNING Account(Id, Name)').",
                        "examples": [
                            "FIND {Acme} IN NAME FIELDS RETURNING Account(Name), Contact(FirstName, LastName)",
                            "FIND {support@example.com} IN EMAIL FIELDS RETURNING Contact(Name, Email)",
                            "FIND {SF*} IN ALL FIELDS LIMIT 20"
                        ]
                    },
                },
                "required": ["search"]
            }
        ),
        types.Tool(
            name="get_object_fields",
            description="Retrieves detailed information about the fields of a specific Salesforce object, including their names, labels, data types, and other properties. This tool is useful for understanding the structure of an object and its fields, which can be essential for data integration, migration, or custom application development.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "The API name of the Salesforce object for which to retrieve field information. Examples of valid object names include 'Account', 'Contact', 'Opportunity', 'MyCustomObject__c', or any other custom or standard object in your Salesforce org.",
                        "examples": [
                            "Account",
                            "Opportunity",
                            "Lead",
                            "My_Custom_Object__c"
                        ]
                    },
                },
                "required": ["object_name"]
            }
        ),
        types.Tool(
            name="create_record",
            description="Creates a new record for a specified object.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "The API name of the object to create a record for (e.g., 'Account', 'Contact').",
                        "examples": ["Account", "Lead", "Task"]
                    },
                    "data": {
                        "type": "object",
                        "description": "A dictionary containing the field API names and values for the new record.",
                        "properties": {},
                        "additionalProperties": True,
                        "examples": [
                            {"Name": "New Lead Inc.", "Company": "New Lead Company", "Status": "Open - Not Contacted"}, # For Lead
                            {"Name": "Sample Account", "BillingStreet": "123 Main St", "BillingCity": "Anytown"}, # For Account
                            {"Subject": "Follow up call", "Status": "Not Started", "Priority": "Normal"} # For Task
                        ]
                    }
                },
                "required": ["object_name", "data"]
            }
        ),
        types.Tool(
            name="update_record",
            description="Updates an existing record specified by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "The API name of the object to update.",
                        "examples": ["Contact", "Opportunity", "Case"]
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The 15 or 18 character ID of the record to update.",
                        "examples": ["003...", "006...", "500..."]
                    },
                    "data": {
                        "type": "object",
                        "description": "A dictionary containing the field API names and new values.",
                        "properties": {},
                        "additionalProperties": True,
                        "examples": [
                            {"Phone": "(555) 123-4567", "Title": "VP of Sales"}, # For Contact
                            {"StageName": "Prospecting", "Probability": 10}, # For Opportunity
                            {"Status": "Working", "Priority": "High"} # For Case
                        ]
                    }
                },
                "required": ["object_name", "record_id", "data"]
            }
        ),
        types.Tool(
            name="delete_record",
            description="Deletes a record specified by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "The API name of the object to delete from.",
                        "examples": ["Lead", "Task", "My_Temp_Object__c"]
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The 15 or 18 character ID of the record to delete.",
                        "examples": ["00Q...", "00T...", "a01..."]
                    },
                },
                "required": ["object_name", "record_id"]
            }
        ),
    ]
    
    return tools

