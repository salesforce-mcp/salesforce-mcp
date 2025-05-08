import asyncio

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

import mcp.server.stdio

import salesforcemcp.sfdc_client as sfdc_client
import salesforcemcp.definitions as sfmcpdef
import salesforcemcp.implementations as sfmcpimpl
    
server = Server("salesforce-mcp")

sf_client = sfdc_client.OrgHandler()
if not sf_client.establish_connection():
    print("Failed to initialize Salesforce connection")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Dynamically excludes tools requiring a live connection if sf_client is not connected.
    """

    all_tools = sfmcpdef.get_tools()
    is_connected = sf_client.metadata_cache is not None

    if is_connected:
        return all_tools
    else:
        print("Salesforce connection inactive. Filtering available tools.")
        live_connection_tools = {
            "create_record", "delete_object_fields", "create_tab", "create_custom_app"
        }
        available_tools = [tool for tool in all_tools if tool.name not in live_connection_tools]
        return available_tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, str]) -> list[types.TextContent]:
    if name == "create_object":
        return sfmcpimpl.create_object_impl(sf_client, arguments)
    if name == "create_object_with_fields":
        return sfmcpimpl.create_object_with_fields_impl(sf_client, arguments)
    if name == "create_custom_field":
        return sfmcpimpl.create_object_with_fields_impl(sf_client, arguments)
    elif name == "delete_object_fields":
        return sfmcpimpl.delete_object_fields_impl(sf_client, arguments)
    elif name == "create_tab":
        return sfmcpimpl.create_tab_impl(sf_client, arguments)
    elif name == "create_custom_app":
        return sfmcpimpl.create_custom_app_impl(sf_client, arguments)
    elif name == "create_report_folder":
        return sfmcpimpl.create_report_folder_impl(sf_client, arguments)
    elif name == "create_dashboard_folder":
        return sfmcpimpl.create_dashboard_folder_impl(sf_client, arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def run():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="salesforce-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(run())
