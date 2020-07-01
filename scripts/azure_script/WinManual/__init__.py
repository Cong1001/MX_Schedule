from azure.common.client_factory import get_client_from_cli_profile 
from azure.mgmt.compute import ComputeManagementClient   
from subscriptions import switch_sub
from common import send_command

def generate_win_check_cmd():    
    run_command_parameters = {    
    'command_id': 'RunPowerShellScript',     
    'script': [    
        'if (Get-Module -ListAvailable -Name PSWindowsUpdate) {}',    
        'else {Install-Module PSWindowsUpdate -Force}',    
        '$updates=Get-WindowsUpdate',    
        'foreach ($update in $updates) {if ($update.Title -Match "Cumulative Update for Windows Server"){$update.KB}}'    
    ]    
}    
    return run_command_parameters

def generate_download_cmd(win_excludes_list, exclude_KBs_dict):
    ps_run_cmd_parameters = {
        'command_id': 'RunPowerShellScript',
        'script': [
            "if ((Test-Path -Path C:\\updates) -ne 'True') {New-Item -Path 'C:\\' -Name 'updates' -ItemType 'directory'}"
        ]
    }
    for KB in win_excludes_list:
        if KB in exclude_KBs_dict.keys():
            KB_download_cmd = "Invoke-WebRequest -Uri " + exclude_KBs_dict[KB] + " -OutFile C:\\updates\\" + KB + ".msu"
            ps_run_cmd_parameters['script'].append(KB_download_cmd)
    return ps_run_cmd_parameters

def get_win_excludes(run_cmd, windows_vm_name):    
    if run_cmd.status() == "Succeeded":
        for message in run_cmd.result().as_dict()["value"]:
            if message['code'] == 'ComponentStatus/StdOut/succeeded' and message['message'] != '':
                KBs_list = message['message'].split('\n')
    return KBs_list

def get_excludes_KBs_dict(vm_excludes_dict):
    excludes_dict = {}
    for sub in vm_excludes_dict.keys():
        for vm in vm_excludes_dict[sub]:
            win_type = (vm_excludes_dict[sub][vm]["Patch Group"].split('-'))[0]
            print(win_type)
            if win_type not in excludes_dict.keys():
                excludes_dict[win_type] = {}

    for sub in vm_excludes_dict.keys():
        for vm in vm_excludes_dict[sub]:
            win_type = (vm_excludes_dict[sub][vm]["Patch Group"].split('-'))[0]
            for KB in vm_excludes_dict[sub][vm]['excludes']:
                if KB != '' and KB not in excludes_dict[win_type].keys():
                    excludes_dict[win_type][KB] = ''
    print(excludes_dict)

    for win_type in list(excludes_dict):
        add_mark = 'Y'
        print(win_type + " excludes infor:")
        if excludes_dict[win_type] != {}:
            for KB in excludes_dict[win_type]:
                KB_url = input("Please input " + KB + " download URL: ")
                excludes_dict[win_type][KB] = KB_url

        while add_mark == 'Y':
            add_mark = input("Is there addition exclude KB for " + win_type + " ?(Y/N): ")
            if add_mark == 'Y':
                add_KB = input("Please input KB number(KBXXXXXXX): ")
                add_KB_url = input("Please input KB download URL: ")
                excludes_dict[win_type][add_KB] = add_KB_url
        if excludes_dict[win_type] == {}:
            excludes_dict.pop(win_type)
    return excludes_dict