import shutil
import os
import base64
from simple_salesforce import Salesforce
from typing import Optional, Any
import xml.etree.ElementTree as ET

BASE_PATH=os.getenv("BASE_PATH"),

class OrgHandler:
    """Manages interactions and caching for a Salesforce org."""

    def __init__(self):
        self.connection: Optional[Salesforce] = None
        self.metadata_cache: dict[str, Any] = {}

    def establish_connection(self) -> bool:
        """Initiates and authenticates the connection to the Salesforce org.

        Returns:
            bool: Returns True upon successful authentication, False otherwise.
        """
        try:
            self.connection = Salesforce(
                username=os.getenv("USERNAME"),
                password=os.getenv("PASSWORD"),
                security_token=os.getenv("SECURITY_TOKEN")
            )
            return True
        except Exception as e:
            print(f"Failed to establish Salesforce connection: {str(e)}")
            self.connection = None
            return False

def write_to_file(content):
    with open(f"{BASE_PATH}/mylog.txt", 'a') as f:
        f.write(content)

def create_metadata_package(json_obj):

    name = json_obj["name"]
    plural_name = json_obj["plural_name"]
    description = json_obj["description"]
    api_name = json_obj["api_name"]
    fields = json_obj["fields"]

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except:
        print("the current directory doesn't exist")

    source = f"{BASE_PATH}/assets/create_object_tmpl/"
    destination = f"{BASE_PATH}/current/"

    shutil.copytree(source, destination)

    old_name = f"{BASE_PATH}/current/objects/##api_name##.object"
    new_name = f"{BASE_PATH}/current/objects/{api_name}.object"

    os.rename(old_name, new_name)

    with open(f"{BASE_PATH}/assets/field.tmpl", "r", encoding="utf-8") as file:
        field_tmpl = file.read()

    fields_str = ""

    for field in fields:
        f_name = field["label"]
        f_type = field["type"]
        type_def = ""
        if f_type == "Text":
            type_def = """
    <type>Text</type>
    <length>100</length>"""
        else:
            type_def = """<precision>18</precision>
    <scale>0</scale>
    <type>Number</type>"""

        f_api_name = field["api_name"]
        new_field = field_tmpl.replace("##api_name##", f_api_name)
        new_field = new_field.replace("##name##", f_name)
        new_field = new_field.replace("##type##", type_def)
        fields_str = fields_str + new_field

    with open(f"{BASE_PATH}/current/package.xml", "r", encoding="utf-8") as file:
        pack_tmpl = file.read()

    pack_tmpl = pack_tmpl.replace("##api_name##", api_name)

    with open(f"{BASE_PATH}/current/package.xml", "w", encoding="utf-8") as file:
        file.write(pack_tmpl)

    obj_path = f"{BASE_PATH}/current/objects/{api_name}.object"

    with open(obj_path, "r", encoding="utf-8") as file:
        obj_tmpl = file.read()

    obj_tmpl = obj_tmpl.replace("##description##", description)
    obj_tmpl = obj_tmpl.replace("##name##", name)
    obj_tmpl = obj_tmpl.replace("##plural_name##", plural_name)
    obj_tmpl = obj_tmpl.replace("##fields##", fields_str)

    with open(obj_path, "w", encoding="utf-8") as file:
        file.write(obj_tmpl)

def create_class_package(json_obj):

    class_name = json_obj["class_name"]
    class_body = json_obj["class_body"]

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return  # Stop if we can't clear the directory

    source = f"{BASE_PATH}/assets/create_class_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return # Stop if template copying fails

    old_cls_name = f"{destination}/classes/##class_name##.cls"
    new_cls_name = f"{destination}/classes/{class_name}.cls"
    old_meta_name = f"{destination}/classes/##class_name##.cls-meta.xml"
    new_meta_name = f"{destination}/classes/{class_name}.cls-meta.xml"

    try:
        os.rename(old_cls_name, new_cls_name)
        os.rename(old_meta_name, new_meta_name)
    except OSError as e:
        print(f"Error renaming template files: {e}")
        return # Stop if renaming fails

    # Update package.xml
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##class_name##", class_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    try:
        with open(new_cls_name, "w", encoding="utf-8") as file:
            file.write(class_body) # Write the full body provided by the user
    except Exception as e:
        print(f"Error writing .cls file: {e}")
        return

    # Meta file doesn't have placeholders in the current template,
    # but adding a read/write step in case it changes later.
    try:
        with open(new_meta_name, "r", encoding="utf-8") as file:
            meta_tmpl = file.read()
        with open(new_meta_name, "w", encoding="utf-8") as file:
            file.write(meta_tmpl)
    except Exception as e:
        print(f"Error processing .cls-meta.xml file: {e}")
        return

def create_record_type_package(json_obj):
    object_name = json_obj["object_name"]
    record_type_name = json_obj["record_type_name"]
    developer_name = json_obj["developer_name"]
    description = json_obj.get("description", "")
    is_active = json_obj["is_active"]

    # Convert boolean to 'true'/'false' string for XML
    active_str = str(is_active).lower()

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source = f"{BASE_PATH}/assets/create_record_type_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    old_rt_name = f"{destination}/recordTypes/Template.recordType-meta.xml"
    new_rt_name_dir = f"{destination}/recordTypes/"
    new_rt_name_full = f"{new_rt_name_dir}/{object_name}.{developer_name}.recordType-meta.xml"

    try:
        os.makedirs(new_rt_name_dir, exist_ok=True)
        os.rename(old_rt_name, new_rt_name_full)
    except OSError as e:
        print(f"Error renaming template file: {e}")
        return

    package_path = f"{destination}/package.xml"
    full_member_name = f"{object_name}.{developer_name}"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##object_name##.##developer_name##", full_member_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    try:
        with open(new_rt_name_full, "r", encoding="utf-8") as file:
            rt_tmpl = file.read()
        rt_tmpl = rt_tmpl.replace("##developer_name##", developer_name)
        rt_tmpl = rt_tmpl.replace("##is_active##", active_str)
        rt_tmpl = rt_tmpl.replace("##description##", description)
        rt_tmpl = rt_tmpl.replace("##record_type_name##", record_type_name)
        with open(new_rt_name_full, "w", encoding="utf-8") as file:
            file.write(rt_tmpl)
    except Exception as e:
        print(f"Error processing .recordType-meta.xml file: {e}")
        return

def zip_directory(filepath):
    source_directory = filepath
    output_zip_name = f"{BASE_PATH}/pack"
    shutil.make_archive(output_zip_name, 'zip', source_directory)

def binary_to_base64(file_path):
    try:
        with open(file_path, "rb") as binary_file:
            binary_data = binary_file.read()
            base64_encoded = base64.b64encode(binary_data)
            return base64_encoded.decode('utf-8')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

import requests

def deploy(b64, sf):
    """Deploys the zipped package using the provided simple_salesforce connection."""
    if not sf:
         print("Error: Salesforce connection object (sf) not provided to deploy function.")
         raise ValueError("Deployment failed: Invalid Salesforce connection.")

    try:
        session_id = sf.session_id
        # simple-salesforce often stores instance like 'yourinstance.my.salesforce.com'
        # or 'yourinstance.lightning.force.com', ensure it's just the base instance
        instance_url = sf.sf_instance
        if not instance_url:
             raise ValueError("Could not retrieve instance URL from Salesforce connection.")

        # Ensure API version matches package.xml if necessary (using 58.0 here)
        metadata_api_version = "58.0" 
        endpoint = f"https://{instance_url}/services/Soap/m/{metadata_api_version}"
        print(f"Using dynamic endpoint: {endpoint}") # Log the endpoint being used
    except AttributeError as e:
         print(f"Error accessing connection attributes: {e}")
         raise ValueError("Deployment failed: Could not get session details from Salesforce connection.")

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        'SOAPAction': '""'
    }

    xml_body_template = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{session_id}</met:sessionId> <!-- Dynamic Session ID -->
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:deploy>
         <met:ZipFile>{base64_zip}</met:ZipFile>
         <met:DeployOptions>
            <met:allowMissingFiles>false</met:allowMissingFiles>
            <met:autoUpdatePackage>false</met:autoUpdatePackage>
            <met:checkOnly>false</met:checkOnly>
            <met:ignoreWarnings>false</met:ignoreWarnings>
            <met:performRetrieve>false</met:performRetrieve>
            <met:purgeOnDelete>false</met:purgeOnDelete>
            <met:rollbackOnError>true</met:rollbackOnError>
            <met:singlePackage>true</met:singlePackage>
         </met:DeployOptions>
      </met:deploy>
   </soapenv:Body>
</soapenv:Envelope>
    """

    if b64 is None:
        print("Error: Base64 package data is None. Cannot deploy.")
        raise ValueError("Deployment failed: Invalid package data.")

    # Populate the template
    xml_body = xml_body_template.format(session_id=session_id, base64_zip=b64)

    # Log the request body (optional, good for debugging but might log session ID)
    # print(f"SOAP Request Body:\n{xml_body}")
    with open(f"{BASE_PATH}/deploy.log", "w", encoding="utf-8") as file:
        file.write(xml_body)

    try:
        response = requests.post(endpoint, data=xml_body, headers=headers)
        
        print(f"Deployment API Response Status: {response.status_code}")
        print(f"Deployment API Response Text:\n{response.text}")
        with open(f"{BASE_PATH}/deploy_http.log", "w", encoding="utf-8") as file:
            file.write(response.text)

        # --- Add Robust Error Checking --- 
        if response.status_code >= 400:
             # Try to parse for a SOAP fault message for better error reporting
             fault_message = f"HTTP Error {response.status_code}."
             try:
                 root = ET.fromstring(response.text)
                 # Look for soapenv:Fault (adjust namespace prefixes if needed)
                 fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
                 if fault is not None:
                     faultcode = fault.findtext('{*}faultcode')
                     faultstring = fault.findtext('{*}faultstring')
                     fault_message = f"SOAP Fault: Code='{faultcode}', Message='{faultstring}' (HTTP Status: {response.status_code})"
             except ET.ParseError:
                 fault_message += " Additionally, the response body was not valid XML." # Or just use raw text
             except Exception as parse_e:
                 print(f"Minor error parsing SOAP fault: {parse_e}") # Log parsing error but continue
                 fault_message += f" Response Text: {response.text[:500]}..." # Include snippet of raw text
             
             raise ValueError(f"Salesforce deployment API call failed: {fault_message}")
        # Add checks for specific deployment success/failure messages within the SOAP body if needed
        # For now, we assume non-error status code means the deployment was accepted (though it might fail asynchronously)
        print("Deployment request submitted successfully to Salesforce.")
        # --- End Error Checking --- 

    except requests.exceptions.RequestException as req_e:
         print(f"Network error during deployment API call: {req_e}")
         raise ValueError(f"Deployment failed: Network error contacting Salesforce API. Details: {str(req_e)}")
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"Unexpected error during deployment call: {e}")
        raise

def create_send_to_server(sf):
    """Zips the current package and sends it for deployment using the provided sf connection."""
    zip_directory(f"{BASE_PATH}/current")
    b64 = binary_to_base64(f"{BASE_PATH}/pack.zip")
    deploy(b64, sf) # Pass sf connection

def delete_send_to_server(sf):
    """Zips the current delete package and sends it for deployment using the provided sf connection."""
    zip_directory(f"{BASE_PATH}/current_delete")
    b64 = binary_to_base64(f"{BASE_PATH}/pack.zip")
    deploy(b64, sf) # Pass sf connection

def delete_fields(json_obj):
    api_name = json_obj["api_name"]
    fields = json_obj["fields"]

    members = ""

    for field in fields:
        field_name = field["api_name"]
        members = members + f"<members>{api_name}.{field_name}</members>\n"

    try:
        shutil.rmtree(f"{BASE_PATH}/current_delete/")
    except:
        print("the current directory doesn't exist")

    source = f"{BASE_PATH}/assets/delete_fields_tmpl/"
    destination = f"{BASE_PATH}/current_delete/"

    shutil.copytree(source, destination)

    with open(f"{BASE_PATH}/current_delete/destructiveChanges.xml", "r", encoding="utf-8") as file:
        destructive = file.read()

    destructive = destructive.replace("##fields##", members)
        
    with open(f"{BASE_PATH}/current_delete/destructiveChanges.xml", "w", encoding="utf-8") as file:
        file.write(destructive)

def create_report_folder_package(json_obj):
    developer_name = json_obj["developer_name"]
    folder_shares = json_obj.get("folder_shares", []) # Expect list of share dicts

    # Basic validation
    if not developer_name.replace("_", "").isalnum() or " " in developer_name:
         print(f"Invalid developer_name: '{developer_name}'. Use only letters, numbers, and underscores.")
         return

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source = f"{BASE_PATH}/assets/create_report_folder_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    # Rename template file with .reportFolder-meta.xml suffix
    old_folder_meta_name = f"{destination}/reports/Template.folder-meta.xml"
    new_folder_meta_name = f"{destination}/reports/{developer_name}.reportFolder-meta.xml"

    try:
        os.makedirs(os.path.dirname(new_folder_meta_name), exist_ok=True)
        if os.path.exists(old_folder_meta_name):
             os.rename(old_folder_meta_name, new_folder_meta_name)
        else:
             print(f"Warning: Template file {old_folder_meta_name} not found, cannot rename.")
             pass
    except OSError as e:
        print(f"Error preparing template file path: {e}")
        return

    # Update package.xml (Assuming package.xml template uses <name>Report</name>)
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##developer_name##", developer_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    # --- Generate folderShares XML --- 
    shares_xml_parts = []
    for share in folder_shares:
        access_level = share.get("accessLevel")
        shared_to = share.get("sharedTo")
        shared_to_type = share.get("sharedToType")
        if all([access_level, shared_to, shared_to_type]):
            shares_xml_parts.append("    <folderShares>")
            shares_xml_parts.append(f"        <accessLevel>{access_level}</accessLevel>")
            shares_xml_parts.append(f"        <sharedTo>{shared_to}</sharedTo>")
            shares_xml_parts.append(f"        <sharedToType>{shared_to_type}</sharedToType>")
            shares_xml_parts.append("    </folderShares>")
        else:
            print(f"Warning: Skipping invalid folder share definition: {share}")
    shares_xml_string = "\n".join(shares_xml_parts)
    # --- End Generate XML --- 

    # --- Process the Report Folder Meta XML using the template --- 
    try:
        with open(new_folder_meta_name, "r", encoding="utf-8") as file:
            folder_tmpl = file.read()

        folder_tmpl = folder_tmpl.replace("##developer_name##", developer_name)
        # Replace placeholder comment with actual shares XML
        folder_tmpl = folder_tmpl.replace("<!-- ##folder_shares_placeholder## -->", shares_xml_string)

        # Remove potentially empty lines left by placeholder replacement if no shares
        folder_tmpl = "\n".join(line for line in folder_tmpl.splitlines() if line.strip())

        with open(new_folder_meta_name, "w", encoding="utf-8") as file:
            file.write(folder_tmpl)
    except Exception as e:
        print(f"Error processing .reportFolder-meta.xml file: {e}")
        return

def create_dashboard_folder_package(json_obj):
    developer_name = json_obj["developer_name"]
    folder_shares = json_obj.get("folder_shares", []) # Expect list of share dicts

    # Basic validation
    if not developer_name.replace("_", "").isalnum() or " " in developer_name:
         print(f"Invalid developer_name: '{developer_name}'. Use only letters, numbers, and underscores.")
         return

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source = f"{BASE_PATH}/assets/create_dashboard_folder_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    # Rename template file with .dashboardFolder-meta.xml suffix
    old_folder_meta_name = f"{destination}/dashboards/Template.folder-meta.xml"
    new_folder_meta_name = f"{destination}/dashboards/{developer_name}.dashboardFolder-meta.xml"

    try:
        os.makedirs(os.path.dirname(new_folder_meta_name), exist_ok=True)
        if os.path.exists(old_folder_meta_name):
            os.rename(old_folder_meta_name, new_folder_meta_name)
        else:
            print(f"Warning: Template file {old_folder_meta_name} not found, cannot rename.")
            pass
    except OSError as e:
        print(f"Error preparing template file path: {e}")
        return

    # Update package.xml (Assuming package.xml template uses <name>Dashboard</name>)
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##developer_name##", developer_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    # --- Generate folderShares XML --- 
    shares_xml_parts = []
    for share in folder_shares:
        access_level = share.get("accessLevel")
        shared_to = share.get("sharedTo")
        shared_to_type = share.get("sharedToType")
        if all([access_level, shared_to, shared_to_type]):
            shares_xml_parts.append("    <folderShares>")
            shares_xml_parts.append(f"        <accessLevel>{access_level}</accessLevel>")
            shares_xml_parts.append(f"        <sharedTo>{shared_to}</sharedTo>")
            shares_xml_parts.append(f"        <sharedToType>{shared_to_type}</sharedToType>")
            shares_xml_parts.append("    </folderShares>")
        else:
            print(f"Warning: Skipping invalid folder share definition: {share}")
    shares_xml_string = "\n".join(shares_xml_parts)
    # --- End Generate XML --- 

    try:
        with open(new_folder_meta_name, "r", encoding="utf-8") as file:
            folder_tmpl = file.read()

        folder_tmpl = folder_tmpl.replace("##developer_name##", developer_name)
        # Replace placeholder comment with actual shares XML
        folder_tmpl = folder_tmpl.replace("<!-- ##folder_shares_placeholder## -->", shares_xml_string)

        folder_tmpl = "\n".join(line for line in folder_tmpl.splitlines() if line.strip())

        with open(new_folder_meta_name, "w", encoding="utf-8") as file:
            file.write(folder_tmpl)
    except Exception as e:
        print(f"Error processing .dashboardFolder-meta.xml file: {e}")
        return

def create_report_type_package(json_obj):
    developer_name = json_obj["developer_name"]
    label = json_obj["label"]
    base_object = json_obj["base_object"]
    description = json_obj.get("description", "")
    sections = json_obj.get("sections", []) # Expects a list of section dicts

    # --- Generate Sections XML --- 
    sections_xml_parts = []
    for section in sections:
        section_label = section.get("label", "")
        columns = section.get("columns", [])
        
        # --- Generate Columns XML for this section --- 
        current_section_columns_xml = []
        for column in columns:
            field_name = column.get("field")
            table_name = column.get("table")
            if field_name and table_name:
                 # Each column gets its own <columns> wrapper
                 current_section_columns_xml.append(f"        <columns>")
                 current_section_columns_xml.append(f"            <checkedByDefault>true</checkedByDefault>")
                 current_section_columns_xml.append(f"            <field>{field_name}</field>")
                 current_section_columns_xml.append(f"            <table>{table_name}</table>")
                 current_section_columns_xml.append(f"        </columns>")
            else:
                print(f"Warning: Skipping invalid column definition in section '{section_label}': {column}")
        # --- End Generate Columns XML ---

        if current_section_columns_xml: # Only add section if it has valid columns
            sections_xml_parts.append(f"    <sections>")
            sections_xml_parts.extend(current_section_columns_xml) # Add the individual <columns> blocks
            sections_xml_parts.append(f"        <masterLabel>{section_label}</masterLabel>")
            sections_xml_parts.append(f"    </sections>")
        else:
             print(f"Warning: Skipping section '{section_label}' as it has no valid columns.")
             
    sections_xml_string = "\n".join(sections_xml_parts)
    # --- End Generate Sections XML ---

    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source = f"{BASE_PATH}/assets/create_report_type_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    # Rename template file
    old_rt_meta_name = f"{destination}/reportTypes/Template.reportType-meta.xml"
    new_rt_meta_name = f"{destination}/reportTypes/{developer_name}.reportType-meta.xml"

    try:
        # Explicitly ensure the target directory exists
        os.makedirs(os.path.dirname(new_rt_meta_name), exist_ok=True)
        os.rename(old_rt_meta_name, new_rt_meta_name)
    except OSError as e:
        print(f"Error renaming template file: {e}")
        return

    # Update package.xml
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##developer_name##", developer_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    # Update report type meta file (.reportType-meta.xml)
    try:
        with open(new_rt_meta_name, "r", encoding="utf-8") as file:
            rt_tmpl = file.read()
        
        rt_tmpl = rt_tmpl.replace("##label##", label)
        rt_tmpl = rt_tmpl.replace("##description##", description)
        rt_tmpl = rt_tmpl.replace("##base_object##", base_object)
        rt_tmpl = rt_tmpl.replace("##sections_xml##", sections_xml_string)
        
        with open(new_rt_meta_name, "w", encoding="utf-8") as file:
            file.write(rt_tmpl)
    except Exception as e:
        print(f"Error processing .reportType-meta.xml file: {e}")
        return

def create_tab_package(json_obj):
    tab_api_name = json_obj["tab_api_name"]
    tab_type = json_obj["tab_type"]
    label = json_obj["label"]
    motif = json_obj.get("motif")
    description = json_obj.get("description")
    object_name = json_obj.get("object_name")
    vf_page_name = json_obj.get("vf_page_name")
    web_url = json_obj.get("web_url")
    url_encoding_key = json_obj.get("url_encoding_key", "UTF8")

    # --- Basic Validation (keep this) --- 
    valid_types = ['CustomObject', 'VisualforcePage', 'Web']
    if tab_type not in valid_types:
        print(f"Invalid tab_type: {tab_type}. Must be one of {valid_types}")
        return
    if tab_type == 'CustomObject' and tab_api_name != object_name:
         print(f"Error: For CustomObject tabs, tab_api_name ('{tab_api_name}') must match the object_name ('{object_name}')")
         return
    if tab_type == 'VisualforcePage' and not vf_page_name:
        print(f"Error: vf_page_name is required for VisualforcePage tabs.")
        return
    if tab_type == 'Web' and not web_url:
        print(f"Error: web_url is required for Web tabs.")
        return
    # Add motif format validation if needed

    # --- Prepare Environment (keep this) --- 
    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source = f"{BASE_PATH}/assets/create_tab_tmpl/"
    destination = f"{BASE_PATH}/current/"

    try:
        shutil.copytree(source, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    # Define target filename
    new_tab_meta_name = f"{destination}/tabs/{tab_api_name}.tab-meta.xml"
    # Ensure the target directory exists
    try:
        os.makedirs(os.path.dirname(new_tab_meta_name), exist_ok=True)
    except OSError as e:
        print(f"Error creating target directory: {e}")
        return

    # We can delete the copied template file as we won't use it
    old_tab_meta_name = f"{destination}/tabs/Template.tab-meta.xml"
    if os.path.exists(old_tab_meta_name):
        try:
            os.remove(old_tab_meta_name)
        except OSError as e:
             print(f"Warning: Could not remove template file {old_tab_meta_name}: {e}")

    # --- Update package.xml (keep this) --- 
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##tab_api_name##", tab_api_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    # --- Manually Construct Tab Meta XML --- 
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">',
        f'    <label>{label}</label>',
        f'    <motif>{motif}</motif>'
    ]
    
    # Add type-specific tag
    if tab_type == 'CustomObject':
        xml_lines.append('    <customObject>true</customObject>')
    elif tab_type == 'VisualforcePage':
        xml_lines.append(f'    <page>{vf_page_name}</page>')
    elif tab_type == 'Web':
        xml_lines.append(f'    <url>{web_url}</url>')
        xml_lines.append(f'    <urlEncodingKey>{url_encoding_key}</urlEncodingKey>')
        
    # Add optional description
    if description:
        xml_lines.append(f'    <description>{description}</description>')
        
    xml_lines.append('</CustomTab>')
    
    final_xml_content = "\n".join(xml_lines)
    # --- End XML Construction --- 

    # --- Write Constructed XML to File --- 
    try:
        # --- Add Debug Print --- 
        print("--- Writing Tab Meta XML ---")
        print(final_xml_content)
        print("--- End Tab Meta XML ---")
        # --- End Debug Print ---
        with open(new_tab_meta_name, "w", encoding="utf-8") as file:
            file.write(final_xml_content)
    except Exception as e:
        print(f"Error writing .tab-meta.xml file: {e}")
        return
    # --- End Write XML ---

def create_report_package(json_obj):
    """Prepares a package to deploy a single report using parameters and a template.

    Args:
        json_obj (dict): Contains structured report parameters like report_name, 
                         folder_name, display_name, report_type, format, 
                         columns (list), groupings_down (list).
    """
    # Extract parameters
    report_name = json_obj.get("report_name")
    folder_name = json_obj.get("folder_name")
    display_name = json_obj.get("display_name")
    report_type = json_obj.get("report_type")
    report_format = json_obj.get("format", "Tabular") # Default to Tabular
    columns = json_obj.get("columns", [])
    groupings_down = json_obj.get("groupings_down", [])

    # Basic validation
    if not all([report_name, folder_name, display_name, report_type, columns]):
        print("Error: Missing required report parameters: report_name, folder_name, display_name, report_type, columns.")
        return
    if report_format not in ["Tabular", "Summary"]:
         print(f"Error: Invalid format '{report_format}'. Only 'Tabular' and 'Summary' supported currently.")
         return
    if report_format == "Summary" and not groupings_down:
         print("Error: 'groupings_down' are required for 'Summary' format reports.")
         return
    if report_format == "Tabular" and groupings_down:
        print("Warning: 'groupings_down' provided but will be ignored for 'Tabular' format report.")
        groupings_down = [] # Clear groupings for Tabular

    # --- Prepare environment --- 
    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    destination = f"{BASE_PATH}/current/"
    os.makedirs(destination, exist_ok=True)

    # --- Update package.xml --- 
    package_template_path = f"{BASE_PATH}/assets/create_report_tmpl/package.xml"
    package_dest_path = f"{destination}/package.xml"
    try:
        with open(package_template_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##folder_name##", folder_name)
        pack_tmpl = pack_tmpl.replace("##report_name##", report_name)
        with open(package_dest_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except FileNotFoundError:
         print(f"Error: package.xml template not found at {package_template_path}")
         return
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return

    # --- Prepare Report XML using Template --- 
    report_template_path = f"{BASE_PATH}/assets/create_report_tmpl/reports/Template.report-meta.xml"
    report_folder_path = f"{destination}/reports/{folder_name}/"
    report_file_path = f"{report_folder_path}/{report_name}.report-meta.xml"

    try:
        os.makedirs(report_folder_path, exist_ok=True)
    except OSError as e:
        print(f"Error creating report directory structure: {e}")
        return

    try:
        with open(report_template_path, "r", encoding="utf-8") as file:
            report_tmpl = file.read()

        # Replace simple placeholders
        report_tmpl = report_tmpl.replace("##display_name##", display_name)
        report_tmpl = report_tmpl.replace("##report_type##", report_type)
        report_tmpl = report_tmpl.replace("##format##", report_format)

        # Generate columns XML
        columns_xml_parts = []
        for col_field in columns:
            if isinstance(col_field, str) and col_field.strip(): # Basic check
                columns_xml_parts.append(f"    <columns><field>{col_field.strip()}</field></columns>")
            else:
                 print(f"Warning: Skipping invalid column definition: {col_field}")
        columns_xml_string = "\n".join(columns_xml_parts)
        report_tmpl = report_tmpl.replace("<!-- ##columns_placeholder## -->", columns_xml_string)

        # Generate groupings XML (only if format is Summary)
        groupings_xml_string = ""
        if report_format == "Summary":
            groupings_xml_parts = []
            for group_field in groupings_down:
                 if isinstance(group_field, str) and group_field.strip():
                      # Assuming default granularity and sort order for now
                      groupings_xml_parts.append(f"    <groupingsDown>")
                      groupings_xml_parts.append(f"        <dateGranularity>Day</dateGranularity>") # Hardcoded
                      groupings_xml_parts.append(f"        <field>{group_field.strip()}</field>")
                      groupings_xml_parts.append(f"        <sortOrder>Asc</sortOrder>") # Hardcoded
                      groupings_xml_parts.append(f"    </groupingsDown>")
                 else:
                      print(f"Warning: Skipping invalid grouping definition: {group_field}")
            groupings_xml_string = "\n".join(groupings_xml_parts)
            
        report_tmpl = report_tmpl.replace("<!-- ##groupings_down_placeholder## -->", groupings_xml_string)

        # Placeholder for filters - replace with empty for now
        report_tmpl = report_tmpl.replace("<!-- ##filters_placeholder## -->", "")

        # Clean up potentially empty lines from removed placeholders
        report_tmpl = "\n".join(line for line in report_tmpl.splitlines() if line.strip())

        # Write the final XML
        with open(report_file_path, "w", encoding="utf-8") as file:
            file.write(report_tmpl)
        print(f"Report XML generated and written to: {report_file_path}")

    except FileNotFoundError:
        print(f"Error: Report template not found at {report_template_path}")
        return
    except Exception as e:
        print(f"Error processing report template or writing file: {e}")
        return

def create_custom_app_package(json_obj):
    """Prepares a package to deploy a single Custom Application.

    Args:
        json_obj (dict): Contains app parameters like api_name, label, nav_type, tabs, etc.
    """
    # Extract parameters
    api_name = json_obj.get("api_name")
    label = json_obj.get("label")
    nav_type = json_obj.get("nav_type", "Standard") # Default to Standard
    tabs = json_obj.get("tabs", [])
    description = json_obj.get("description", "")
    header_color = json_obj.get("header_color") # Optional
    form_factors = json_obj.get("form_factors", ["Small", "Large"]) # Default
    setup_experience = json_obj.get("setup_experience", "all") # Default

    # Basic validation
    if not all([api_name, label, tabs]):
        print("Error: Missing required app parameters: api_name, label, tabs.")
        return
    if nav_type not in ["Standard", "Console"]:
        print(f"Warning: Invalid nav_type '{nav_type}'. Defaulting to Standard.")
        nav_type = "Standard"
    if not isinstance(tabs, list) or not all(isinstance(t, str) for t in tabs):
         print("Error: 'tabs' parameter must be a list of strings (tab API names).")
         return
    if not isinstance(form_factors, list) or not all(f in ["Small", "Large"] for f in form_factors):
        print("Warning: Invalid form_factors. Defaulting to ['Small', 'Large'].")
        form_factors = ["Small", "Large"]

    # --- Prepare environment --- 
    try:
        shutil.rmtree(f"{BASE_PATH}/current/")
    except FileNotFoundError:
        print("The 'current' directory doesn't exist, proceeding.")
    except Exception as e:
        print(f"Error removing directory: {e}")
        return

    source_tmpl_dir = f"{BASE_PATH}/assets/create_custom_app_tmpl/"
    destination = f"{BASE_PATH}/current/"
    try:
        shutil.copytree(source_tmpl_dir, destination)
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return
        
    # Rename app template file
    old_app_file = f"{destination}/applications/Template.app-meta.xml"
    new_app_file = f"{destination}/applications/{api_name}.app-meta.xml"
    try:
        # Ensure directory exists (needed if copytree didn't create it fully)
        os.makedirs(os.path.dirname(new_app_file), exist_ok=True) 
        os.rename(old_app_file, new_app_file)
    except OSError as e:
        print(f"Error renaming app template file: {e}")
        return
        
    # --- Update package.xml --- 
    package_path = f"{destination}/package.xml"
    try:
        with open(package_path, "r", encoding="utf-8") as file:
            pack_tmpl = file.read()
        pack_tmpl = pack_tmpl.replace("##api_name##", api_name)
        with open(package_path, "w", encoding="utf-8") as file:
            file.write(pack_tmpl)
    except Exception as e:
        print(f"Error processing package.xml: {e}")
        return
        
    # --- Prepare App XML using Template --- 
    try:
        with open(new_app_file, "r", encoding="utf-8") as file:
            app_tmpl = file.read()
            
        # Replace simple placeholders
        app_tmpl = app_tmpl.replace("##label##", label)
        app_tmpl = app_tmpl.replace("##nav_type##", nav_type)
        app_tmpl = app_tmpl.replace("##description##", description)
        app_tmpl = app_tmpl.replace("##setup_experience##", setup_experience)
        
        # Generate brand XML (optional)
        brand_xml = ""
        if header_color:
             # Basic color validation could be added here (#ABCDEF format)
             brand_xml = f"    <brand>\n        <headerColor>{header_color}</headerColor>\n        <shouldOverrideOrgTheme>true</shouldOverrideOrgTheme>\n    </brand>"
        app_tmpl = app_tmpl.replace("<!-- ##brand_placeholder## -->", brand_xml)
        
        # Generate form factors XML
        form_factors_xml = "\n".join([f"    <formFactors>{ff}</formFactors>" for ff in form_factors])
        app_tmpl = app_tmpl.replace("<!-- ##form_factors_placeholder## -->", form_factors_xml)
        
        # Generate tabs XML
        tabs_xml = "\n".join([f"    <tabs>{tab}</tabs>" for tab in tabs])
        app_tmpl = app_tmpl.replace("<!-- ##tabs_placeholder## -->", tabs_xml)

        # Clean up potentially empty lines from removed placeholders
        app_tmpl = "\n".join(line for line in app_tmpl.splitlines() if line.strip())

        # Write the final XML
        with open(new_app_file, "w", encoding="utf-8") as file:
            file.write(app_tmpl)
        print(f"Custom App XML generated and written to: {new_app_file}")
            
    except Exception as e:
        print(f"Error processing app template or writing file: {e}")
        return

