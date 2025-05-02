import mcp.types as types

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
                    "fields": {
                        "type": "array",
                        "description": "The fields of the object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["Text", "Number", "Lookup", "LongText"],
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
                        },
                        "additionalProperties": True,
                    },
                },
                "required": ["name" "plural_name", "api_name", "fields"],
            },
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
        )
    ]

    return tools

