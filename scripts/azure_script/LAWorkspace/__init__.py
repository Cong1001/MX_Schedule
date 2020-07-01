import time

def create_or_update_workspace(log_client, ws_rg, ws_name, region):
    ws_parameters = {
        'location': region,
        'sku': {
            'name': 'pergb2018'
        },
        'retention_in_days': 30
    }
    create_update_ws = log_client.workspaces.create_or_update(ws_rg, ws_name, ws_parameters)
    time.sleep(30)
    ws_result = (create_update_ws.result()).as_dict()
    return ws_result

def generate_extension_parameter(extension_name, workspace_id, workspace_key, region):
    extension_parameter = {
        'location': region,
        'publisher': 'Microsoft.EnterpriseCloud.Monitoring',
        'type_handler_version': '1.0',
        'virtual_machine_extension_type': extension_name,
        'auto_upgrade_minor_version': True,
        "settings": {
            "workspaceId": workspace_id
        },
        "protectedSettings": {
            "workspaceKey": workspace_key
        }
    }
    return extension_parameter

def check_extension_status(compute_client, vm_rg, vm_name, extension_name):
    extension_status = 'Unsucceeded'
    extensions = compute_client.virtual_machine_extensions.list(vm_rg, vm_name)
    if extensions.as_dict()['value'] != []:
        for extension in extensions.as_dict()['value']:
            if extension['virtual_machine_extension_type'] == extension_name and extension['provisioning_state'] == 'Succeeded':
                extension_status = 'Succeeded'
    return extension_status

def vm_connect_workspace(compute_client, vm_rg, vm_name, extension_name, extension_parameters):
    add_extension = compute_client.virtual_machine_extensions.create_or_update(vm_rg, vm_name, extension_name, extension_parameters)
#    add_extension.wait()
#    extension_status = add_extension.status()
#    return extension_status

def generate_ws_aa_link_parameters(ws_name, aa_resource_id, aa_location):
    parameters = {
        "omsWorkspaceName": {
            "value": ws_name
        },
        "accountResourceId": {
            "value": aa_resource_id
        },
        "workspaceLocation": {
            "value": aa_location
        }
    }
    return parameters
