import salesforcemcp.sfdc_client as sfdc_client
from salesforcemcp.sfdc_client import OrgHandler
import mcp.types as types
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError# import metadata API helper classes
import json
from simple_salesforce import SalesforceError
from typing import Any

def create_object_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    """Creates a new custom object via the Salesforce Tooling API using the simple-salesforce client."""
    name = arguments.get("name")
    plural_name = arguments.get("plural_name")
    api_name = arguments.get("api_name")

    if not sf_client.connection:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Salesforce connection is not active. Cannot perform metadata deployment.")],
            isError=True
        )

    mdapi=sf_client.connection.mdapi

    custom_object = mdapi.CustomObject(
    fullName = api_name,
    label = name,
    pluralLabel =plural_name,
    nameField = mdapi.CustomField(
        label = "Name",
        type = mdapi.FieldType("Text")
    ),
    deploymentStatus = mdapi.DeploymentStatus("Deployed"),
    sharingModel = mdapi.SharingModel("Read")
)
    try:
        mdapi.CustomObject.create(custom_object)
    except SalesforceError as e:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error creating custom object: {e}")],
            isError=True
        )

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Custom Object '{api_name}' created successfully")],
        isError=True
    )

def create_object_with_fields_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    name = arguments.get("name")
    plural_name = arguments.get("plural_name")
    api_name = arguments.get("api_name")
    description = arguments.get("description")
    fields = arguments.get("fields")

    json_obj = {}
    json_obj["name"] = name
    json_obj["plural_name"] = plural_name
    json_obj["api_name"] = api_name
    json_obj["description"] = description
    json_obj["fields"] = fields

    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot perform metadata deployment.")
    sfdc_client.write_to_file(json.dumps(json_obj))
    sfdc_client.create_metadata_package(json_obj)
    sfdc_client.create_send_to_server(sf_client.connection)

    return [
        types.TextContent(
            type="text",
            text=f"Custom Object '{api_name}' creation package prepared and deployment initiated."
        )
    ]

def create_field_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    return create_object_impl(sf_client, arguments)

def delete_object_fields_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    api_name = arguments.get("api_name")
    fields = arguments.get("fields")

    json_obj = {}
    json_obj["api_name"] = api_name
    json_obj["fields"] = fields

    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot perform metadata deployment.")
    sfdc_client.delete_fields(json_obj)
    sfdc_client.delete_send_to_server(sf_client.connection)

    return [
        types.TextContent(
            type="text",
            text=f"Delete Object fields on '{api_name}' creation package prepared and deployment initiated."
        )
    ]

def create_tab_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    args = arguments
    tab_api_name = args.get("tab_api_name")
    label = args.get("label")
    motif = args.get("motif")
    tab_type = args.get("tab_type")
    object_name = args.get("object_name")
    vf_page_name = args.get("vf_page_name")
    web_url = args.get("web_url")
    url_encoding_key = args.get("url_encoding_key", "UTF8")
    description = args.get("description")

    if not all([tab_api_name, label, motif, tab_type]):
        raise ValueError("Missing required arguments: tab_api_name, label, motif, tab_type")

    valid_types = ['CustomObject', 'VisualforcePage', 'Web']
    if tab_type not in valid_types:
        raise ValueError(f"Invalid tab_type: '{tab_type}'. Must be one of {valid_types}")
    if tab_type == 'CustomObject' and not object_name:
         raise ValueError("object_name is required when tab_type is 'CustomObject'")
    if tab_type == 'CustomObject' and tab_api_name != object_name:
         # This validation is also in sfdc_client, but good to have early check
         raise ValueError("For CustomObject tabs, tab_api_name must match object_name")
    if tab_type == 'VisualforcePage' and not vf_page_name:
        raise ValueError("vf_page_name is required when tab_type is 'VisualforcePage'")
    if tab_type == 'Web' and not web_url:
        raise ValueError("web_url is required when tab_type is 'Web'")
        
    json_obj = {
        "tab_api_name": tab_api_name,
        "label": label,
        "motif": motif,
        "tab_type": tab_type,
        "object_name": object_name, # Will be None if not provided
        "vf_page_name": vf_page_name,
        "web_url": web_url,
        "url_encoding_key": url_encoding_key,
        "description": description
    }

    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot perform metadata deployment.")

    try:
        sfdc_client.create_tab_package(json_obj)
        sfdc_client.create_send_to_server(sf_client.connection)
        return [
            types.TextContent(
                type="text",
                text=f"Custom Tab '{tab_api_name}' creation package prepared and deployment initiated."
            )
        ]
    except Exception as e:
        print(f"Error during Custom Tab creation/deployment: {e}")
        raise ValueError(f"Failed to create or deploy Custom Tab '{tab_api_name}'. Error: {str(e)}")

def create_custom_metadata_type_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    """Creates a new Custom Metadata Type via the Metadata API."""
    api_name = arguments.get("api_name")
    label = arguments.get("label")
    plural_name = arguments.get("plural_name")
    description = arguments.get("description", "")
    fields = arguments.get("fields")

    # Validate required inputs
    missing = []
    for arg in ("api_name", "label", "plural_name", "fields"):
        if not arguments.get(arg):
            missing.append(arg)
    if missing:
        return [types.TextContent(type="text", text=f"Missing required argument(s): {', '.join(missing)}")]

    if not sf_client.connection:
        raise ValueError("Salesforce connection not active. Cannot deploy custom metadata type.")

    # Prepare and deploy metadata package for Custom Metadata Type
    json_obj = {
        "name": label,
        "plural_name": plural_name,
        "description": description,
        "api_name": api_name,
        "fields": fields
    }
    # Use the Custom Metadata Type package generator
    sfdc_client.create_custom_metadata_type_package(json_obj)
    # Deploy the prepared package (deployment_package) via the Metadata API
    sfdc_client.deploy_package_from_deploy_dir(sf_client.connection)
    return [types.TextContent(type="text", text=f"Custom Metadata Type '{api_name}' creation package prepared and deployment initiated.")]

def create_custom_app_impl(sf_client: OrgHandler, arguments: dict[str, str]):
    """
    Creates a new custom application and optionally assigns visibility to specified profiles.
    Arguments:
        api_name: API name of the app
        label: Label for the app
        nav_type: Navigation type
        tabs: List of tab API names
        description: App description
        header_color: Header color
        form_factors: List of form factors
        setup_experience: Setup experience
        visible_profiles: (optional) List of profile API names to grant app visibility
    """
    api_name = arguments.get("api_name")
    label = arguments.get("label")
    nav_type = arguments.get("nav_type", "Standard")
    tabs = arguments.get("tabs")
    description = arguments.get("description")
    header_color = arguments.get("header_color")
    form_factors = arguments.get("form_factors", ["Small", "Large"])
    setup_experience = arguments.get("setup_experience", "all")
    visible_profiles = arguments.get("visible_profiles", [])

    if not all([api_name, label, isinstance(tabs, list)]):
        raise ValueError("Missing required arguments: api_name, label, tabs (must be a list)")
    if not api_name.replace("_", "").isalnum() or " " in api_name:
        raise ValueError(f"Invalid api_name: '{api_name}'. Use only letters, numbers, and underscores.")

    json_obj = {
        "api_name": api_name,
        "label": label,
        "nav_type": nav_type,
        "tabs": tabs,
        "description": description,
        "header_color": header_color,
        "form_factors": form_factors,
        "setup_experience": setup_experience
    }

    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot perform metadata deployment.")

    try:
        sfdc_client.create_custom_app_package(json_obj)
        sfdc_client.create_send_to_server(sf_client.connection)
        return [
            types.TextContent(
                type="text",
                text=f"Custom Application '{api_name}' creation package prepared and deployment initiated."
            )
        ]
    except Exception as e:
        print(f"Error during Custom Application creation/deployment: {e}")
        raise ValueError(f"Failed to create or deploy Custom Application '{api_name}'. Error: {str(e)}")

def create_report_folder_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    """Creates a new Salesforce report folder by inserting a Folder record via the REST API."""
    folder_api_name = arguments.get("folder_api_name")
    folder_label = arguments.get("folder_label")
    access_type = arguments.get("access_type", "Private")
    if not folder_api_name or not folder_label:
        return [types.TextContent(type="text", text="Missing 'folder_api_name' or 'folder_label'.")]
    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot create folder.")
    data = {
        "DeveloperName": folder_api_name,
        "Name": folder_label,
        "AccessType": access_type,
        "Type": "Report"
    }
    try:
        result = sf_client.connection.Folder.create(data)
        if result.get("success"):
            return [types.TextContent(
                type="text",
                text=(
                    f"Report folder '{folder_label}' (API Name: {folder_api_name}) created successfully. "
                    f"(Id: {result.get('id')})"
                )
            )]
        else:
            errors = "; ".join(result.get("errors", []))
            return [types.TextContent(type="text", text=f"Failed to create folder: {errors}")]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"Salesforce Error creating folder: {e.status} {e.content}")]
    except Exception as e:
        raise ValueError(f"Unexpected error creating folder: {e}")

def create_dashboard_folder_impl(sf_client: sfdc_client.OrgHandler, arguments: dict[str, str]):
    """Creates a new Salesforce dashboard folder by inserting a Folder record via the REST API."""
    folder_api_name = arguments.get("folder_api_name")
    folder_label = arguments.get("folder_label")
    access_type = arguments.get("access_type", "Private")
    # Validate inputs
    if not folder_api_name or not folder_label:
        return [types.TextContent(type="text", text="Missing 'folder_api_name' or 'folder_label'.")]
    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot create dashboard folder.")
    # Prepare Folder record
    data = {
        "DeveloperName": folder_api_name,
        "Name": folder_label,
        "AccessType": access_type,
        "Type": "Dashboard"
    }
    try:
        result = sf_client.connection.Folder.create(data)
        if result.get("success"):
            return [types.TextContent(
                type="text",
                text=(
                    f"Dashboard folder '{folder_label}' (API Name: {folder_api_name}) created successfully. "
                    f"(Id: {result.get('id')})"
                )
            )]
        else:
            errors = "; ".join(result.get("errors", []))
            return [types.TextContent(type="text", text=f"Failed to create dashboard folder: {errors}")]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"Salesforce Error creating dashboard folder: {e.status} {e.content}")]
    except Exception as e:
        raise ValueError(f"Unexpected error creating dashboard folder: {e}")

def create_lightning_page_impl(sf_client, arguments):
    """Creates a new Lightning App Page in Salesforce with a unique name."""
    try:
        page_label = arguments.get("label", "Simple Lightning App Page")
        description = arguments.get("description", "")
        ok = sfdc_client.deploy_lightning_page(page_label, description)
        if not ok:
            return [types.TextContent(type="text", text="Failed to create Lightning Page package.")]
        sfdc_client.deploy_package_from_deploy_dir(sf_client.connection)
        return [types.TextContent(type="text", text=f"Successfully created new Lightning App Page with label: {page_label}!")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating Lightning App Page: {str(e)}")]

# --- Data Operations ---

def run_soql_query_impl(sf_client: OrgHandler, arguments: dict[str, str]):
    query = arguments.get("query")
    if not query:
        raise ValueError("Missing 'query' argument")
    if not sf_client.connection:
        raise ValueError("Salesforce connection not established.")
    try:
        results = sf_client.connection.query_all(query)
        # Consider limits on result size? Truncate or summarize if too large?
        return [
            types.TextContent(
                type="text",
                text=f"SOQL Query Results (JSON):\\n{json.dumps(results, indent=2)}"
            )
        ]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"SOQL Error: {e.status} {e.resource_name} {e.content}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error executing SOQL: {e}")]

def run_sosl_search_impl(sf_client: OrgHandler, arguments: dict[str, str]):
    search = arguments.get("search")
    if not search:
        raise ValueError("Missing 'search' argument")
    if not sf_client.connection:
        raise ValueError("Salesforce connection not established.")
    try:
        results = sf_client.connection.search(search)
        return [
            types.TextContent(
                type="text",
                text=f"SOSL Search Results (JSON):\\n{json.dumps(results, indent=2)}"
            )
        ]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"SOSL Error: {e.status} {e.resource_name} {e.content}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error executing SOSL: {e}")]

def get_object_fields_impl(sf_client: OrgHandler, arguments: dict[str, str]):
    object_name = arguments.get("object_name")
    if not object_name:
        raise ValueError("Missing 'object_name' argument")
    try:
        # Use the caching method from OrgHandler
        results = sf_client.get_object_fields_cached(object_name)
        return [
            types.TextContent(
                type="text",
                text=f"{object_name} Fields Metadata (JSON):\\n{json.dumps(results, indent=2)}"
            )
        ]
    except Exception as e: # Catches errors from get_object_fields_cached
         return [types.TextContent(type="text", text=f"Error getting fields for {object_name}: {e}")]

def create_record_impl(sf_client: OrgHandler, arguments: dict[str, Any]): # Data can be complex
    object_name = arguments.get("object_name")
    data = arguments.get("data")
    if not object_name or not data:
        raise ValueError("Missing 'object_name' or 'data' argument")
    if not sf_client.connection:
        raise ValueError("Salesforce connection not established.")
    if not isinstance(data, dict):
         raise ValueError("'data' argument must be a dictionary/object.")
    try:
        sf_object = getattr(sf_client.connection, object_name)
        results = sf_object.create(data)
        # Result usually {'id': '...', 'success': True, 'errors': []}
        return [
            types.TextContent(
                type="text",
                text=f"Create {object_name} Record Result (JSON):\\n{json.dumps(results, indent=2)}"
            )
        ]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"Create Record Error: {e.status} {e.resource_name} {e.content}")]
    except AttributeError:
         return [types.TextContent(type="text", text=f"Error: Object type '{object_name}' not found or accessible via API.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating {object_name} record: {e}")]

def update_record_impl(sf_client: OrgHandler, arguments: dict[str, Any]):
    object_name = arguments.get("object_name")
    record_id = arguments.get("record_id")
    data = arguments.get("data")
    if not object_name or not record_id or not data:
        raise ValueError("Missing 'object_name', 'record_id', or 'data' argument")
    if not sf_client.connection:
        raise ValueError("Salesforce connection not established.")
    if not isinstance(data, dict):
         raise ValueError("'data' argument must be a dictionary/object.")
    try:
        sf_object = getattr(sf_client.connection, object_name)
        # Update returns status code (204 No Content on success)
        status_code = sf_object.update(record_id, data)
        success = 200 <= status_code < 300
        message = f"Update {object_name} record {record_id}: Status Code {status_code} - {'Success' if success else 'Failed'}"
        return [types.TextContent(type="text", text=message)]
    except SalesforceError as e:
        return [types.TextContent(type="text", text=f"Update Record Error: {e.status} {e.resource_name} {e.content}")]
    except AttributeError:
         return [types.TextContent(type="text", text=f"Error: Object type '{object_name}' not found or accessible via API.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error updating {object_name} record {record_id}: {e}")]

def delete_record_impl(sf_client: OrgHandler, arguments: dict[str, str]):
    object_name = arguments.get("object_name")
    record_id = arguments.get("record_id")
    if not object_name or not record_id:
        raise ValueError("Missing 'object_name' or 'record_id' argument")
    if not sf_client.connection:
        raise ValueError("Salesforce connection not established.")
    try:
        sf_object = getattr(sf_client.connection, object_name)
        # Delete returns status code (204 No Content on success)
        status_code = sf_object.delete(record_id)
        success = 200 <= status_code < 300
        message = f"Delete {object_name} record {record_id}: Status Code {status_code} - {'Success' if success else 'Failed'}"
        return [types.TextContent(type="text", text=message)]
    except SalesforceError as e:
        # Handle common delete errors (e.g., protected record)
        return [types.TextContent(type="text", text=f"Delete Record Error: {e.status} {e.resource_name} {e.content}")]
    except AttributeError:
         return [types.TextContent(type="text", text=f"Error: Object type '{object_name}' not found or accessible via API.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error deleting {object_name} record {record_id}: {e}")]

def describe_object_impl(sf_client: OrgHandler, arguments: dict[str, Any]):
    """
    Get detailed schema information for a Salesforce object, formatted as markdown.
    Args:
        sf_client: OrgHandler instance with an active Salesforce connection
        arguments: dict with keys:
            - object_name (str): API name of the object (e.g., 'Account')
            - include_field_details (bool, optional): Whether to include detailed field info (default True)
    Returns:
        List with a single types.TextContent containing the markdown schema description or error message.
    """
    object_name = arguments.get("object_name")
    include_field_details = arguments.get("include_field_details", True)
    if not object_name:
        return [types.TextContent(type="text", text="Missing 'object_name' argument")]  
    if not sf_client.connection:
        return [types.TextContent(type="text", text="Salesforce connection not established.")]
    try:
        sf_object = getattr(sf_client.connection, object_name)
        describe = sf_object.describe()
        # Basic object info
        result = f"## {describe['label']} ({describe['name']})\n\n"
        result += f"**Type:** {'Custom Object' if describe.get('custom') else 'Standard Object'}\n"
        result += f"**API Name:** {describe['name']}\n"
        result += f"**Label:** {describe['label']}\n"
        result += f"**Plural Label:** {describe.get('labelPlural', '')}\n"
        result += f"**Key Prefix:** {describe.get('keyPrefix', 'N/A')}\n"
        result += f"**Createable:** {describe.get('createable')}\n"
        result += f"**Updateable:** {describe.get('updateable')}\n"
        result += f"**Deletable:** {describe.get('deletable')}\n\n"
        if include_field_details:
            # Fields table
            result += "## Fields\n\n"
            result += "| API Name | Label | Type | Required | Unique | External ID |\n"
            result += "|----------|-------|------|----------|--------|------------|\n"
            for field in describe["fields"]:
                required = "Yes" if not field.get("nillable", True) else "No"
                unique = "Yes" if field.get("unique", False) else "No"
                external_id = "Yes" if field.get("externalId", False) else "No"
                result += f"| {field['name']} | {field['label']} | {field['type']} | {required} | {unique} | {external_id} |\n"
            # Relationship fields
            reference_fields = [
                f for f in describe["fields"] if f["type"] == "reference" and f.get("referenceTo")
            ]
            if reference_fields:
                result += "\n## Relationship Fields\n\n"
                result += "| API Name | Related To | Relationship Name |\n"
                result += "|----------|-----------|-------------------|\n"
                for field in reference_fields:
                    related_to = ", ".join(field["referenceTo"])
                    rel_name = field.get("relationshipName", "N/A")
                    result += f"| {field['name']} | {related_to} | {rel_name} |\n"
            # Picklist fields
            picklist_fields = [
                f for f in describe["fields"]
                if f["type"] in ("picklist", "multipicklist") and f.get("picklistValues")
            ]
            if picklist_fields:
                result += "\n## Picklist Fields\n\n"
                for field in picklist_fields:
                    result += f"### {field['label']} ({field['name']})\n\n"
                    result += "| Value | Label | Default |\n"
                    result += "|-------|-------|--------|\n"
                    for value in field["picklistValues"]:
                        is_default = "Yes" if value.get("defaultValue", False) else "No"
                        result += f"| {value['value']} | {value['label']} | {is_default} |\n"
                    result += "\n"
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error describing object {object_name}: {str(e)}")]

def define_tabs_on_app_impl(sf_client: OrgHandler, arguments: dict[str, Any]):
    """
    Defines or updates the tabs for an existing Lightning app.
    
    Args:
        sf_client: OrgHandler instance with an active Salesforce connection
        arguments: dict with keys:
            - app_api_name (str): API name of the existing app
            - tabs (list): List of tab API names to include in the app
            - append (bool, optional): If True, append to existing tabs. If False, replace existing tabs.
    """
    app_api_name = arguments.get("app_api_name")
    tabs = arguments.get("tabs")
    append = arguments.get("append", False)

    if not app_api_name or not isinstance(tabs, list):
        raise ValueError("Missing required arguments: app_api_name and tabs (must be a list)")

    if not sf_client.connection:
        raise ValueError("Salesforce connection is not active. Cannot update app tabs.")

    try:
        # First, retrieve the current app metadata
        mdapi = sf_client.connection.mdapi
        app_metadata = mdapi.CustomApplication.read(app_api_name)
        
        if not app_metadata:
            raise ValueError(f"App '{app_api_name}' not found")

        # Get current tabs if appending
        current_tabs = []
        if append and hasattr(app_metadata, 'tabs'):
            current_tabs = app_metadata.tabs

        # Combine or replace tabs
        new_tabs = current_tabs + tabs if append else tabs

        # Update the app metadata
        app_metadata.tabs = new_tabs
        mdapi.CustomApplication.update(app_metadata)

        return [
            types.TextContent(
                type="text",
                text=f"Successfully updated tabs for app '{app_api_name}'. New tab configuration: {', '.join(new_tabs)}"
            )
        ]

    except Exception as e:
        raise ValueError(f"Error updating app tabs: {str(e)}")
