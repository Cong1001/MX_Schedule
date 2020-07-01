#!/usr/bin/env python3.6

import json, math, sys, ast, os
from settings import GetSettings
from assume import crossaccount_session
from Check import check_baseline_file, get_dev_cron, get_prd_cron, dev_datetime, prd_datetime
from aws_ec2 import get_group_list, get_dev_group_list, get_prd_group_list
from aws_s3 import get_s3_bucket_name, get_s3_folder_name, s3_bucket_create
from BaselineManager import CheckBaseline, CreateLinuxBaseline, CreateWindowsBaseline, UpdateLinuxBaseline, UpdateWindowsBaseline, RegisterBaselineForPatchGroup
from MXSchedule import CheckWindow, CreateWindow, UpdateWindow, CheckTarget, RegisterTarget, UpdateTarget, CheckTask, RegisterTask, UpdateTask, RegisterLinuxRunCMD, UpdateLinuxRunCMD

def AWS_Schedule(account_id, account_name, account_region):
#Get parameters
    print("******************************************* %s *******************************************" %account_name)
    session = crossaccount_session(account_id)
    ec2 = session.client('ec2', region_name=account_region)
    ssm = session.client('ssm', region_name=account_region)
    s3 = session.client('s3', region_name=account_region)
    settings = GetSettings()
    dev_window_name = settings.dev_window_name
    prd_window_name = settings.prd_window_name
    task_name = settings.task_name
    dev_cron = get_dev_cron()
    prd_cron = get_prd_cron()
    dev_time = dev_datetime()
    prd_time = prd_datetime()
    linux_cache_clean_name = settings.linux_cacheclean_task
    linux_cache_clean_cmd = settings.linux_cacheclean_cmd
    
    s3_bucket = get_s3_bucket_name(account_name)
    s3_dev_folder = get_s3_folder_name(dev_time)
    s3_prd_folder = get_s3_folder_name(prd_time)
    
#Check S3 bucket, for saving logs
    s3_bucket_create(s3, account_name, account_region)
        
#Get Patch Groups
    group_list = get_group_list(ec2, ssm)
    if group_list == []:
        print("######################################################################")
        print("# ERROR: No Patch Group catched, please add 'Patch Group' tag first! #")
        print("######################################################################")
        no_tag_list_file = settings.no_tag_tmp_file
        with open(no_tag_list_file, 'a') as no_tag_list:
            no_tag_list.write('Customer ID: ' + account_name + '\n')
        no_tag_list.close()
        return None
    dev_group_list = get_dev_group_list(group_list)
    prd_group_list = get_prd_group_list(group_list)
    
#Create/Update Baselines
    for group in group_list:
        BaselineID = CheckBaseline(ssm, group)
        BaselineSettingsFile = open(check_baseline_file(), 'r')
        BaselineSettings = json.load(BaselineSettingsFile)
        group_os = (group.split('-')[0])
        OS = BaselineSettings[group_os]['OS']
        product = BaselineSettings[group_os]['Product']
        severity = BaselineSettings[group_os]['Severity']
        classification = BaselineSettings[group_os]['Classification']
        rejectpatches = BaselineSettings[group_os]['Reject_Patchs']
        if BaselineID == 'None':
            if group[:3] == 'Win':
                BaselineID = CreateWindowsBaseline(ssm, OS, group, product, severity, classification, rejectpatches)
            else:
                BaselineID = CreateLinuxBaseline(ssm, OS, group, product, severity, classification, rejectpatches)
        else:
            if group[:3] == 'Win':
                UpdateWindowsBaseline(ssm, BaselineID, group, product, severity, classification, rejectpatches)
            else:
                UpdateLinuxBaseline(ssm, BaselineID, group, product, severity, classification, rejectpatches)
        RegisterBaselineForPatchGroup(ssm, BaselineID, group)
        

#Schedule DEV Maintenance Window
    if len(dev_group_list) == 0:
        print("No dev/qa/uat... Linux servers or Windows servers, skip DEV_Maintenance_Window schedule.")
    else:
        dev_group_num = int(math.ceil(len(dev_group_list)/5.0))
        dev_Window_ID = CheckWindow(ssm, dev_window_name)
        if dev_Window_ID == 'None':
            dev_Window_ID = CreateWindow(ssm, dev_window_name, dev_cron)
        else:
            UpdateWindow(ssm, dev_Window_ID, dev_window_name, dev_cron)
        if dev_group_num > 1:
            dev_mw_targets = []
            for i in range(1, dev_group_num):
                dev_group_list_i = dev_group_list[(i-1)*5:5]
                target_name = "Patch_Group_" + str(i)
                target_ID = CheckTarget(ssm, dev_Window_ID, target_name)
                if target_ID == 'None':
                    target_ID = RegisterTarget(ssm, dev_Window_ID, target_name, dev_group_list_i)
                else:
                    UpdateTarget(ssm, dev_Window_ID, target_ID, target_name, dev_group_list_i)
                dev_mw_targets.append(target_ID)
            dev_group_list_i = dev_group_list[(dev_group_num-1)*5:]
            target_name = "Patch_Group_" + str(dev_group_num)
            target_ID = CheckTarget(ssm, dev_Window_ID, target_name)
            if target_ID == 'None':
                target_ID = RegisterTarget(ssm, dev_Window_ID, target_name, dev_group_list_i)
            else:
                UpdateTarget(ssm, dev_Window_ID, target_ID, target_name, dev_group_list_i)
            dev_mw_targets.append(target_ID)
        else:
            dev_mw_targets = []
            target_name = 'Patch_Group_1'
            target_ID = CheckTarget(ssm, dev_Window_ID, target_name)
            if target_ID == 'None':
                target_ID = RegisterTarget(ssm, dev_Window_ID, target_name, dev_group_list)
            else:
                UpdateTarget(ssm, dev_Window_ID, target_ID, target_name, dev_group_list)
            dev_mw_targets.append(target_ID)
        dev_Task_ID = CheckTask(ssm, dev_Window_ID, task_name)
        if dev_Task_ID == 'None':
            RegisterTask(ssm, dev_Window_ID, task_name, dev_mw_targets, s3_bucket, s3_dev_folder)
        else:
            UpdateTask(ssm, dev_Window_ID, dev_Task_ID, task_name, dev_mw_targets, s3_bucket, s3_dev_folder)

        dev_linux_cacheclean_ID = CheckTask(ssm, dev_Window_ID, linux_cache_clean_name)
        if dev_linux_cacheclean_ID == 'None':
            RegisterLinuxRunCMD(ssm, dev_Window_ID, linux_cache_clean_name, dev_mw_targets, s3_bucket, s3_dev_folder, linux_cache_clean_cmd)
        else:
            UpdateLinuxRunCMD(ssm, dev_Window_ID, dev_linux_cacheclean_ID, linux_cache_clean_name, dev_mw_targets, s3_bucket, s3_dev_folder, linux_cache_clean_cmd)

#Schedule PRD Maintenance Window
    if len(prd_group_list) == 0:
        print("No production Linux servers, skip PRD_Maintenance_Window schedule.")
    else:
        prd_group_num = int(math.ceil(len(prd_group_list)/5.0))
        prd_Window_ID = CheckWindow(ssm, prd_window_name)
        if prd_Window_ID == 'None':
            prd_Window_ID = CreateWindow(ssm, prd_window_name, prd_cron)
        else:
            UpdateWindow(ssm, prd_Window_ID, prd_window_name, prd_cron)
        if prd_group_num > 1:
            prd_mw_targets = []
            for i in range(1, prd_group_num):
                prd_group_list_i = prd_group_list[(i-1)*5:5]
                target_name = "Patch_Group_" + str(i)
                target_ID = CheckTarget(ssm, prd_Window_ID, target_name)
                if target_ID == 'None':
                    target_ID = RegisterTarget(ssm, prd_Window_ID, target_name, prd_group_list_i)
                else:
                    UpdateTarget(ssm, prd_Window_ID, target_ID, target_name, prd_group_list_i)
                prd_mw_targets.append(target_ID)
            prd_group_list_i = prd_group_list[(prd_group_num-1)*5:]
            target_name = "Patch_Group_" + str(prd_group_num)
            target_ID = CheckTarget(ssm, prd_Window_ID, target_name)
            if target_ID == 'None':
                target_ID = RegisterTarget(ssm, prd_Window_ID, target_name, prd_group_list_i)
            else:
                UpdateTarget(ssm, prd_Window_ID, target_ID, target_name, prd_group_list_i)
            prd_mw_targets.append(target_ID)
        else:
            prd_mw_targets = []
            target_name = 'Patch_Group_1'
            target_ID = CheckTarget(ssm, prd_Window_ID, target_name)
            if target_ID == 'None':
                target_ID = RegisterTarget(ssm, prd_Window_ID, target_name, prd_group_list)
            else:
                UpdateTarget(ssm, prd_Window_ID, target_ID, target_name, prd_group_list)
            prd_mw_targets.append(target_ID)
        prd_Task_ID = CheckTask(ssm, prd_Window_ID, task_name)
        if prd_Task_ID == 'None':
            RegisterTask(ssm, prd_Window_ID, task_name, prd_mw_targets, s3_bucket, s3_prd_folder)
        else:
            UpdateTask(ssm, prd_Window_ID, prd_Task_ID, task_name, prd_mw_targets, s3_bucket, s3_prd_folder)

        prd_linux_cacheclean_ID = CheckTask(ssm, prd_Window_ID, linux_cache_clean_name)
        if prd_linux_cacheclean_ID == 'None':
            RegisterLinuxRunCMD(ssm, prd_Window_ID, linux_cache_clean_name, prd_mw_targets, s3_bucket, s3_prd_folder, linux_cache_clean_cmd)
        else:
            UpdateLinuxRunCMD(ssm, prd_Window_ID, prd_linux_cacheclean_ID, linux_cache_clean_name, prd_mw_targets, s3_bucket, s3_prd_folder, linux_cache_clean_cmd)

if __name__ == '__main__':
    settings = GetSettings()
    CustomerID = settings.CustomerID
    fail_list_file = settings.fail_tmp_file
    if CustomerID == None:
        print("Customer ID is not set. Exiting this script.")
        with open(fail_list_file, 'a') as fail_list:
            fail_list.write('Customer ID: Not set!' + '\n' + 'Error info: Customer ID is not set, please enter a valid Customer ID. i.g "C390EUW1"')
        fail_list.close()
    else:
        customer_list_dir = os.walk(settings.aws_customer_list_dir)
        for path,dir_list,file_list in customer_list_dir:
            for file_name in file_list:
                if file_name != ".gitkeep" and file_name != "Exception_List.json": 
                    file_dir = os.path.join(path, file_name)
                    Customer_File = open(file_dir, 'r')
                    account_list = json.loads(Customer_File.read())
                    if CustomerID.upper() in account_list.keys():
                        account_id = account_list[CustomerID.upper()]['ID']
                        account_name = account_list[CustomerID.upper()]['Name']
                        account_region = account_list[CustomerID.upper()]['Region']
                        try:
                            AWS_Schedule(account_id, account_name, account_region)
                        except:
                            print('ERROR: schedule ' + account_name + ' error!')
                            e = sys.exc_info()[1]
                            print("%s" %e)
                            with open(fail_list_file, 'a') as fail_list:
                                fail_list.write('Customer ID: ' + account_name + '\n' + 'Error info: ' + str(e) + '\n')
                            fail_list.close()
                        Customer_File.close()
                        sys.exit(0)
        print("%s is not in Customer List, please add it first!" %CustomerID)
        with open(fail_list_file, 'a') as fail_list:
            fail_list.write('Customer ID: ' + CustomerID + '\n' + 'Error info: ' + CustomerID + ' is not in Customer List, please add it first!' + '\n')
        fail_list.close()
