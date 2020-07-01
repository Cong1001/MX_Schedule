import time, uuid
from settings import GetSettings
from AutoAccount import create_or_update_automation_account

def run_cmd_mx_deploy(compute_client, resource_client, auto_client, log_client, graph_client, auth_client, env, win_excludes, vms_dict, base64_value, sub_id, startTime):
    settings = GetSettings()
    win_scheduler_name = settings.windows_scheduler_name
    lin_scheduler_name = settings.linux_scheduler_name
    Manual_MX_dict = settings.Manual_MX_dict

    resource_group = env
    region = vms_dict[list(vms_dict.keys())[0]]["location"]
    auto_account_name = env
    auto_account_region = region
    linux_list = []
    windows_list = []

#create automation account if it is not exist
    try:
        auto_client.automation_account.get(resource_group, auto_account_name)
        print("Automation account already exist, no need to create!")
    except:
        create_or_update_automation_account(auto_client, resource_group, auto_account_name, auto_account_region)
        print("Created automation account successfully!")

#create and publish Linux_MX_Runbook&Windows_MX_Runbook
    for runbook_name in Manual_MX_dict.keys():
        content_link = Manual_MX_dict[runbook_name]['playbook']
        draft_content_link = auto_client.runbook.models.ContentLink(uri=content_link)
        runbook_Servers_parameter = auto_client.runbook.models.RunbookParameter(type='System.String', is_mandatory=True, position=0)
        runbook_ResourceGroup_parameter = auto_client.runbook.models.RunbookParameter(type='System.String', is_mandatory=True, position=1)
        runbook_draft_parameters = {"Servers": runbook_Servers_parameter, "ResourceGroup": runbook_ResourceGroup_parameter}
        runbook_draft = auto_client.runbook.models.RunbookDraft(draft_content_link=draft_content_link, parameters=runbook_draft_parameters)
        runbook_parameters = auto_client.runbook.models.RunbookCreateOrUpdateParameters(runbook_type="PowerShell", location=auto_account_region, log_verbose=False, log_progress=False, draft=runbook_draft)
        auto_client.runbook.create_or_update(resource_group, auto_account_name, runbook_name, runbook_parameters)
        auto_client.runbook.publish(resource_group, auto_account_name, runbook_name)
        print("Upload / Update " + runbook_name + " successfully!")

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
            app_create_parameters = {'available_to_other_tenants': False, 'display_name': principal_name, 'identifier_uris': ['http://' + principal_name]}
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

    for vm in vms_dict.keys():
        if vms_dict[vm]["Patch Group"][0:3] == "Win":
            windows_list.append(vms_dict[vm]["id"])
        else:
            linux_list.append(vms_dict[vm]["id"])

    if len(windows_list) != 0:
        win_shce_pro = {'name': win_scheduler_name, 'start_time': startTime, 'is_enabled': True, 'frequency': 'OneTime'}
        auto_client.schedule.create_or_update(resource_group, auto_account_name, win_scheduler_name, win_shce_pro)

    if len(linux_list) != 0:
        lin_shce_pro = {'name': lin_scheduler_name, 'start_time': startTime, 'is_enabled': True, 'frequency': 'OneTime'}
        auto_client.schedule.create_or_update(resource_group, auto_account_name, lin_scheduler_name, lin_shce_pro)