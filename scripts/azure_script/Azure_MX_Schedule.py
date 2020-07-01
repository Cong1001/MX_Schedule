#!/usr/bin/env python3   
    
import sys, time, json, argparse, os, boto3
from settings import GetSettings
from subscriptions import subscriptions_dict,switch_sub,login_az, logout_az
from azure.common.client_factory import get_client_from_cli_profile    
from azure.mgmt.compute import ComputeManagementClient    
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.automation import AutomationClient    
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.graphrbac import GraphRbacManagementClient
from azure.mgmt.authorization import AuthorizationManagementClient
from CatchAccount import get_account_list
from common import send_command, generate_selfsign_cert_base64_value
from VMCollection import get_linux_dict, get_windows_dict, get_vm_dict
from Get_Win_Exclude_KBs import send_check_run_cmd
from Generate_Win_exclude_KBs import get_vm_excludes_dict, get_excludes_KBs_dict, add_addition_KBs
from Schedule_Deploy import mx_deploy
from WinManual import generate_download_cmd

def Deploy_Azure_MX(sub_name, sub_id, sub_region, excludes_KBs_dict, win_excludes, base64_value, startTime):    
    print("*****************************************************************************************")
    print("*                              Deploying update management                              *")
    print("*****************************************************************************************")

    print("***********Deployting " + sub_name + " MX schedule***********")
    switch_sub(sub_id)    
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    resource_client = get_client_from_cli_profile(ResourceManagementClient)
    auto_client = get_client_from_cli_profile(AutomationClient)
    log_client = get_client_from_cli_profile(LogAnalyticsManagementClient)
    graph_client = get_client_from_cli_profile(GraphRbacManagementClient)
    auth_client = get_client_from_cli_profile(AuthorizationManagementClient)

    windows_dict = get_windows_dict(compute_client, sub_region)
    vm_dict = get_vm_dict(compute_client, sub_region)
    if vm_dict == {}:
        print("There is no running vms with Patch Group tag in customer " + sub_name + " subscrition. Please check it manually!")
        return 0 

    for env in vm_dict.keys():
        print("***********Deployting " + sub_name + " " + env + " MX schedule***********")
        mx_deploy(compute_client, resource_client, auto_client, log_client, graph_client, auth_client, env.lower(), win_excludes, vm_dict[env], base64_value, sub_id, startTime)  

    compute_client.close()   
    auto_client.close()    
    log_client.close()
    resource_client.close()

    if excludes_KBs_dict != {} and windows_dict != {}:
        print("*****************************************************************************************")
        print("*                       Send cmd to download Windows excludes KBs                       *")
        print("*****************************************************************************************")
        for vm_name in windows_dict.keys():
            resource_group = windows_dict[vm_name]['Resource Group']
            win_excludes_list = windows_dict[vm_name]["excludes"]
            KB_excludes_dict = excludes_KBs_dict[windows_dict[vm_name]["Patch Group"].split("-")[0]]
            KB_download_cmd = generate_download_cmd(win_excludes_list, KB_excludes_dict)
            print(KB_download_cmd)
            print("Sending download command to " + vm_name)
            #send_command(compute_client, resource_group, vm_name, KB_download_cmd)
        compute_client.close()

if __name__ == '__main__':
    base64_value = generate_selfsign_cert_base64_value()
    settings = GetSettings()

#az login    
    ssm = boto3.client('ssm', region_name='us-east-1')
    sp = ssm.get_parameter(Name='AzureAutomation', WithDecryption=True)
    CLIENT = json.loads(sp['Parameter']['Value'])['appId']
    KEY = json.loads(sp['Parameter']['Value'])['password']
    TENANT_ID = settings.TENANT_ID
    params = {
        'user': CLIENT,
        'password': KEY,
        'tenant': TENANT_ID
    }
    az_login = login_az(params)
    if az_login != 0:
        print("az login failed!")
        sys.exit(0)

    startTime = settings.Year + '-' + settings.Month + '-' + settings.Day + 'T' + settings.Hour + ':' + settings.Minute + ':00+00:00'
    CustomerID = settings.CustomerID
    fail_list_file = settings.fail_tmp_file
    windows_manual_file = settings.windows_manual_file
    windows_KBs_file = open(windows_manual_file, 'r')
    excludes_KBs_dict = json.load(windows_KBs_file)
    windows_KBs_file.close()
    win_excludes = []
    if excludes_KBs_dict != {}:
        for server in excludes_KBs_dict.keys():
            for KB in excludes_KBs_dict[server].keys():
                win_excludes.append(KB[2:])
    print(excludes_KBs_dict, win_excludes)

    if settings.SingleCustomer == 'true': 
        if CustomerID == None:
            print("Customer ID is not set. Exiting this script.")
            with open(fail_list_file, 'a') as fail_list:
                fail_list.write('Customer ID: Not set!' + '\n' + 'Error info: Customer ID is not set, please enter a valid Customer ID. i.g "C390EUW1"')
            fail_list.close()
            logout_az()
        else:
            customer_list_dir = os.walk(settings.azure_customer_list_dir)
            for path,dir_list,file_list in customer_list_dir:
                for file_name in file_list:
                    if file_name != ".gitkeep" and file_name != "Exception_List.json": 
                        file_dir = os.path.join(path, file_name)
                        Customer_File = open(file_dir, 'r')
                        subs_list = json.loads(Customer_File.read())
                        if CustomerID.upper() in subs_list.keys():
                            sub_id = subs_list[CustomerID.upper()]['ID']
                            sub_name = subs_list[CustomerID.upper()]['Name']
                            sub_region = (subs_list[CustomerID.upper()]['Region'].replace(' ','')).lower()
                            try:
                                Deploy_Azure_MX(sub_name, sub_id, sub_region, excludes_KBs_dict, win_excludes, base64_value, startTime)
                            except:
                                print('ERROR: schedule ' + sub_name + ' error!')
                                e = sys.exc_info()[1]
                                print("%s" %e)
                                with open(fail_list_file, 'a') as fail_list:
                                    fail_list.write('Customer ID: ' + sub_name + '\n' + 'Error info: ' + str(e) + '\n')
                                fail_list.close()
                            Customer_File.close()
                            logout_az()
                            sys.exit(0)
            print("Customer ID not found!")
            logout_az()
    else:
        region = settings.REGION
        CustomerFile = settings.azure_customer_list_dir + '/' + (region.replace(' ', '')).lower() + '.json'
        if os.path.exists(CustomerFile) == True:
            subs_list = get_account_list(CustomerFile, settings.REGION)
            for sub in subs_list:
                sub_id = subs_list[sub]['ID']
                sub_name = subs_list[sub]['Name']
                sub_region = (subs_list[sub]['Region'].replace(' ', '')).lower()
                try:
                    Deploy_Azure_MX(sub_name, sub_id, sub_region, excludes_KBs_dict, win_excludes, base64_value, startTime)
                except:
                    print('ERROR: schedule ' + sub_name + ' error!')
                    e = sys.exc_info()[1]
                    print("%s" %e)
                    with open(fail_list_file, 'a') as fail_list:
                        fail_list.write('Customer ID: ' + sub_name + '\n' + 'Error info: ' + str(e) + '\n')
                    fail_list.close()
            logout_az()
        else:
            print("Customer json file is missing!")
            with open(fail_list_file, 'a') as fail_list:
                fail_list.write('Customer json file is missing!')
            fail_list.close()
            logout_az()