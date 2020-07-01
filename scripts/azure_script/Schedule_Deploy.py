import sys, time, json, argparse, uuid, time
from settings import GetSettings
from LAWorkspace import check_extension_status, generate_extension_parameter, vm_connect_workspace, create_or_update_workspace, generate_ws_aa_link_parameters
from AutoAccount import generate_windows_schedule_properties, generate_linux_schedule_properties, create_or_update_automation_account, create_update_scheduler
from common import template_deploy, generate_ws_aa_link_template
from datetime import datetime
from RunCMD_Schedule_Deploy import run_cmd_mx_deploy

def mx_deploy(compute_client, resource_client, auto_client, log_client, graph_client, auth_client, env, win_excludes, vms_dict, base64_value, sub_id, startTime):   
    settings = GetSettings()
    workspace_mappings = settings.workspace_mappings
    linux_excludes = settings.linux_excludes
    win_scheduler_name = settings.windows_scheduler_name
    lin_scheduler_name = settings.linux_scheduler_name
    true = bool(1)
    false = bool(0)

    region = vms_dict[list(vms_dict.keys())[0]]["location"]
    
    resource_group = env
    auto_account_name = env
    ws_name = env
    linux_list = []
    windows_list = []
        
#define Log Analitics workspace & auto account location
    if region in list(workspace_mappings.keys()):
        ws_region = region
    else:
        print(region + "is not in map list, move to manual steps")
        run_cmd_mx_deploy(compute_client, resource_client, auto_client, log_client, graph_client, auth_client, env, win_excludes, vms_dict, base64_value, sub_id, startTime)
        return 0
    auto_account_region = workspace_mappings[ws_region]
#create or update Log Analytics Workspace and linked up, and enable update management resolution
    try:
        try:
            workspace = log_client.workspaces.get(ws_region, ws_name)
            workspace_id = workspace.customer_id
            print('There is existing workspace, no need to create')
        except:
            workspace = create_or_update_workspace(log_client, resource_group, ws_name, ws_region)
            workspace_id = workspace['customer_id']
        try:
            auto_account = auto_client.automation_account.get(resource_group, auto_account_name)
            print("Automation account already exist, no need to create!")
        except:
            auto_account = create_or_update_automation_account(auto_client, resource_group, auto_account_name, auto_account_region)
            print("Created automation account successfully!")
        print(auto_account)
        auto_linked_ws = (auto_client.linked_workspace.get(resource_group, auto_account_name)).id
        print(auto_linked_ws)
        if auto_linked_ws != {}:
            print(auto_linked_ws.split('/'))
            if (auto_linked_ws.split('/'))[-1] == ws_name:
                print("Automation account already linked with Log Analytic workspace.")
            else:
                print("Automation account linked a wrong workspace!")
        else:
            workspace_key = log_client.workspaces.get_shared_keys(resource_group, ws_name).as_dict()['primary_shared_key']
            ws_aa_link_template = generate_ws_aa_link_template()
            ws_aa_link_parameters = generate_ws_aa_link_parameters(ws_name, auto_account['id'], auto_account_region)
            ws_aa_link_deploy = template_deploy(resource_client, resource_group, 'ws_aa_auto_link', ws_aa_link_template, ws_aa_link_parameters)
            if ws_aa_link_deploy.status() != "Succeeded":
                print("link failed. Status: " + str(ws_aa_link_deploy.status()) + str(ws_aa_link_deploy.result()))
                return 0
    except:
        e = sys.exc_info()[1]
        print(e)
        return 0
    print(workspace, auto_account)
    
#get windows and linux vms list and connect them to Log Analytics workspace
    for vm in vms_dict.keys():
        if vms_dict[vm]["Patch Group"][0:3] == "Win":
            extension_name = 'MicrosoftMonitoringAgent'
            extension_status = check_extension_status(compute_client, resource_group, vm, extension_name)
            if extension_status == 'Succeeded':
                windows_list.append(vms_dict[vm]["id"])
            else:
                extension_parameters = generate_extension_parameter(extension_name, workspace_id, workspace_key, region)
                vm_connect_workspace(compute_client, resource_group, vm, extension_name, extension_parameters)
                windows_list.append(vms_dict[vm]["id"])
#                connect_status = vm_connect_workspace(compute_client, resource_group, vm, extension_name, extension_parameters)
#                if connect_status == 'Succeeded':
#                    windows_list.append(vms_dict[vm]["id"])
#                else:
#                    print(vm + ' connect to ' + workspace['name'] + connect_status)
        else:
            extension_name = 'OmsAgentForLinux'
            extension_status = check_extension_status(compute_client, resource_group, vm, extension_name)
            if extension_status == 'Succeeded':
                linux_list.append(vms_dict[vm]["id"])
            else:
                extension_parameters = generate_extension_parameter(extension_name, workspace_id, workspace_key, region)
                vm_connect_workspace(compute_client, resource_group, vm, extension_name, extension_parameters)
                linux_list.append(vms_dict[vm]["id"])
#                connect_status = vm_connect_workspace(compute_client, resource_group, vm, extension_name, extension_parameters)
#                if connect_status == 'Succeeded':
#                    linux_list.append(vms_dict[vm]["id"])
#                else:
#                    print(vm + ' connect to ' + workspace['name'] + connect_status)
    print("Connecting vms to analytic workspace.")

#create and publish Pre_Windows_Update runbook
    runbook_name = settings.pre_windows_update_runbook
    content_link = settings.content_link
    draft_content_link = auto_client.runbook.models.ContentLink(uri=content_link)
    runbook_VMS_parameter = auto_client.runbook.models.RunbookParameter(type='System.String', is_mandatory=true, position=0)
    runbook_KBIDs_parameter = auto_client.runbook.models.RunbookParameter(type='System.String', is_mandatory=true, position=1)
    runbook_draft_parameters = {"VMS": runbook_VMS_parameter, "KBIDs": runbook_KBIDs_parameter}
    runbook_draft = auto_client.runbook.models.RunbookDraft(draft_content_link=draft_content_link, parameters=runbook_draft_parameters)
    runbook_parameters = auto_client.runbook.models.RunbookCreateOrUpdateParameters(runbook_type="PowerShell", location=auto_account_region, log_verbose=false, log_progress=false, draft=runbook_draft)
    auto_client.runbook.create_or_update(resource_group, auto_account_name, runbook_name, runbook_parameters)
    auto_client.runbook.publish(resource_group, auto_account_name, runbook_name)
    print("Upload / Update Pre_Windows_Script.ps1 successfully!")

#create run as account for automation account
    principal_name = env + "-automation"
    sub_scope = "/subscriptions/" + sub_id
    role_name = "Contributor"
    #update run as account certificate 
    try:
        cert = auto_client.certificate.get(resource_group, auto_account_name, "AzureRunAsCertificate")
        now_datetime = datetime.now()
        if cert.expiry_time.strftime('%Y-%m-%d') < now_datetime.strftime('%Y-%m-%d'):
            cert_parameters = auto_client.certificate.models.CertificateCreateOrUpdateParameters(name="AzureRunAsCertificate", base64_value=base64_value)
            cert = auto_client.certificate.create_or_update(resource_group, auto_account_name, "AzureRunAsCertificate", cert_parameters)
            print("Update automation account certificate successfully!")
    except:
        cert_parameters = auto_client.certificate.models.CertificateCreateOrUpdateParameters(name="AzureRunAsCertificate", base64_value=base64_value)
        cert = auto_client.certificate.create_or_update(resource_group, auto_account_name, "AzureRunAsCertificate", cert_parameters)
        print("Create automation account certificate successfully!")

    #create run as account if not exist
    try:
        auto_client.connection.get(resource_group, auto_account_name, "AzureRunAsConnection")
        print("There is run as account, no need to create... ")
    except:
        app_list = list(graph_client.applications.list(filter="displayName eq '{}'".format(principal_name)))
        if len(app_list) == 1:
            app = app_list[0]
        else:
            app_create_parameters = {'available_to_other_tenants': false, 'display_name': principal_name, 'identifier_uris': ['http://' + principal_name]}
            app = graph_client.applications.create(app_create_parameters)
        principal_list = list(graph_client.service_principals.list(filter="displayName eq '{}'".format(principal_name)))
        if len(principal_list) == 1: 
            principal = principal_list[0]
        else:
            principal_create_parameters = graph_client.service_principals.models.ServicePrincipalCreateParameters(app_id=app.app_id)
            principal = graph_client.service_principals.create(principal_create_parameters)
            time.sleep(30)
        
        roles = list(auth_client.role_definitions.list(sub_scope, filter="roleName eq '{}'".format(role_name)))
        auth_client.role_assignments.create(sub_scope, uuid.uuid4(), {'role_definition_id': roles[0].id, 'principal_id': principal.object_id})
        connection_type = auto_client.connection.models.ConnectionTypeAssociationProperty(name="AzureServicePrincipal")
        field_definition_values = {'ApplicationId': principal.app_id, 'TenantId': principal.app_owner_tenant_id, 'CertificateThumbprint': cert.thumbprint, 'SubscriptionId': sub_id}
        connection_parameters = auto_client.connection.models.ConnectionCreateOrUpdateParameters(connection_type=connection_type, name="AzureRunAsConnection", field_definition_values=field_definition_values)
        auto_client.connection.create_or_update(resource_group, auto_account_name, "AzureRunAsConnection", connection_parameters)
        print("Create automation account run as account successfully!")
    
#create windows scheduler if it is not exist    
    if len(windows_list) != 0:
        win_properties = generate_windows_schedule_properties(windows_list, startTime, win_excludes)    
        print(win_properties)    
        create_update_scheduler(auto_client, resource_group, auto_account_name, win_scheduler_name, win_properties)    
    
#create linux scheduler if it is not exist    
    if len(linux_list) != 0:
        lin_properties = generate_linux_schedule_properties(linux_list, startTime, linux_excludes)    
        print(lin_properties)    
        create_update_scheduler(auto_client, resource_group, auto_account_name, lin_scheduler_name, lin_properties)    
    
