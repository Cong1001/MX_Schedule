import sys

def create_or_update_automation_account(auto_client, auto_account_rg, auto_account_name, region):
    aa_parameters = {
        'location': region,
        'sku': {
            'name': 'Basic'
        }
    }
    auto_account = auto_client.automation_account.create_or_update(auto_account_rg, auto_account_name, aa_parameters)
    auto_account_result = auto_account.as_dict()
    return auto_account_result

def get_update_mgmt(auto_client, auto_account_rg, auto_account_name):    
    try:    
        update_mgmt = auto_client.software_update_configurations.list(auto_account_rg, auto_account_name)    
        return update_mgmt    
    except:    
        print("automation account not exist")    

def generate_linux_schedule_properties(vm_list, startTime, excludes):    
    basic_properties = {    
        "properties": {    
            "updateConfiguration": {    
                "operatingSystem": 'Linux',   
                "linux": {    
                    "included_package_classifications": "Critical,Security,Other",    
                    "excluded_package_name_masks": excludes,    
                    "rebootSetting": "IfRequired"    
                },
                "duration": "PT6H0M",    
                "azureVirtualMachines": vm_list    
            },    
            "scheduleInfo": {    
                "frequency": "OneTime",    
                "startTime": startTime,    
                "timeZone": "UTC"    
            }    
        }    
    }    
    return basic_properties

def generate_windows_schedule_properties(vm_list, startTime, excludes):
    if excludes == []: 
        update_config = {
            "included_update_classifications": "Critical,Security,UpdateRollup,Definition,Updates",    
            "reboot_setting": "IfRequired"    
        }
        basic_properties = {    
            "properties": {    
                "updateConfiguration": {    
                    "operatingSystem": 'Windows',   
                    "windows": update_config,
                    "duration": "PT6H0M",    
                    "azureVirtualMachines": vm_list    
                },    
                "scheduleInfo": {    
                    "frequency": "OneTime",    
                    "startTime": startTime,    
                    "timeZone": "UTC"    
                }    
            }    
        }   
    else: 
        vm_name = (vm_list[0].split("/"))[-1]
        KBs = ""
        for KB in excludes:
            KBs = KBs + ",KB" + KB
        KBs = KBs.lstrip(",")
        update_config = {
            "included_update_classifications": "Critical,Security,UpdateRollup,Definition,Updates",    
            "excluded_kb_numbers": excludes,    
            "reboot_setting": "Always"    
        }
        task_config = {
            "pre_task": {
                "parameters": {
                    "VMNAME": vm_name,
                    "KBIDS": KBs
                },
                "source": "Pre_Windows_Update"
            }
        }

        basic_properties = {    
            "properties": {    
                "updateConfiguration": {    
                    "operatingSystem": 'Windows',   
                    "windows": update_config,
                    "duration": "PT6H0M",    
                    "azureVirtualMachines": vm_list    
                },    
                "scheduleInfo": {    
                    "frequency": "OneTime",    
                    "startTime": startTime,    
                    "timeZone": "UTC"    
                },
                "tasks": task_config    
            }    
        }   

     
    return basic_properties    

def create_update_scheduler(auto_client, auto_account_rg, auto_account_name, scheduler_name, update_properties):    
    try:    
        auto_client.software_update_configurations.create(auto_account_rg, auto_account_name, scheduler_name, update_properties)    
        print("Create " + scheduler_name + " successfully!")    
    except:    
        e = sys.exc_info()[1]    
        print(e)    

def delete_update_scheduler(auto_client, auto_account_rg, auto_account_name, scheduler_name):    
    try:    
        auto_client.software_update_configurations.delete(auto_account_rg, auto_account_name, scheduler_name)    
        print("Delete " + scheduler_name + " successfully!")    
    except:    
        e = sys.exc_info()[1]    
        print(e)    
