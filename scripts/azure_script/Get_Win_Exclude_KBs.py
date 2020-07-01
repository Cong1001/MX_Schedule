from subscriptions import switch_sub
from azure.common.client_factory import get_client_from_cli_profile  
from azure.mgmt.compute import ComputeManagementClient 
from VMCollection import get_windows_dict
from WinManual import generate_win_check_cmd, generate_download_cmd
from common import send_command

def send_check_run_cmd(subs_vm_dict):
    subs_check_run_cmd_dict = {}
    for sub in subs_vm_dict.keys():
        check_run_cmd_dict = {}
        switch_sub(sub)    
        print("*********************", sub, "*********************")
        compute_client = get_client_from_cli_profile(ComputeManagementClient)
        for resource_group in subs_vm_dict[sub].keys():
            for vm in subs_vm_dict[sub][resource_group].keys():
                if subs_vm_dict[sub][resource_group][vm]["Patch Group"][:3] == "Win":
                    windows_vm_pg = subs_vm_dict[sub][resource_group][vm]["Patch Group"]
                    win_check_cmd = generate_win_check_cmd()
                    ps_command = send_command(compute_client, resource_group, vm, win_check_cmd)
                    check_run_cmd_dict[vm] = {"vm_name": vm, "Resource Group": resource_group, "Patch Group": windows_vm_pg, "ps_command": ps_command}

        if check_run_cmd_dict == {}:
            print("There is no Windows server in customer " + sub)
        else:
            subs_check_run_cmd_dict[sub] = check_run_cmd_dict
        
    return subs_check_run_cmd_dict