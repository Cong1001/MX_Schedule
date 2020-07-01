import sys
from subscriptions import switch_sub
from azure.common.client_factory import get_client_from_cli_profile  
from azure.mgmt.compute import ComputeManagementClient 

def get_linux_dict(compute_client):    
    linux_dict = {}    
    vms = compute_client.virtual_machines.list_all()    
    for vm in vms:    
        resource_group_name = str(vm.id.split('/')[4])    
        vm_name = str(vm.name)    
        vm_detail = compute_client.virtual_machines.get(resource_group_name, vm_name, expand="instanceView")    
        try:
            if vm_detail.instance_view.statuses[1].code == "PowerState/running":    
                if vm.tags != None and "Patch Group" in vm.tags.keys():    
                    if vm.tags["Patch Group"][:3] != "Win":    
                        linux_dict[vm_name] = {"vm_name": vm_name, "resource_group": resource_group_name, "id": vm.id, 'Patch Group': vm.tags["Patch Group"], 'location': vm.location}    
        except:
            e = sys.exc_info()[1]
            print(e)
    return linux_dict    

def get_windows_dict(compute_client, sub_location):    
    windows_dict = {}    
    vms = compute_client.virtual_machines.list_all()    
    for vm in vms:    
        resource_group_name = str(vm.id.split('/')[4])    
        vm_name = str(vm.name)    
        vm_detail = compute_client.virtual_machines.get(resource_group_name, vm_name, expand="instanceView")
        try:
            if vm_detail.instance_view.statuses[1].code == "PowerState/running" and sub_location == vm.location:    
                if vm.tags != None and "Patch Group" in vm.tags.keys():    
                    if vm.tags["Patch Group"][:3] == "Win":
                        windows_dict[vm_name] = {"vm_name": vm_name, "resource_group": resource_group_name, "id": vm.id, 'Patch Group': vm.tags["Patch Group"], 'location': vm.location}    
        except:
            e = sys.exc_info()[1]
            print(e)
    return windows_dict    

def get_vm_dict(compute_client, sub_location):
    vm_dict = {}
    vms = compute_client.virtual_machines.list_all()
    for vm in vms:
        resource_group_name = str(vm.id.split('/')[4])    
        vm_name = str(vm.name)    
        vm_detail = compute_client.virtual_machines.get(resource_group_name, vm_name, expand="instanceView")
        try:
            if vm_detail.instance_view.statuses[1].code == "PowerState/running": 
                print(sub_location, vm.location)
                if vm.tags != None and "Patch Group" in vm.tags.keys() and sub_location == vm.location: 
                    if resource_group_name not in vm_dict.keys():
                        vm_dict[resource_group_name] = {}
                    vm_dict[resource_group_name][vm_name] = {"vm_name": vm_name, "id": vm.id, 'Patch Group': vm.tags["Patch Group"], 'location': vm.location}
        except:
            e = sys.exc_info()[1]
            print(e)
    compute_client.close()
    return vm_dict
    