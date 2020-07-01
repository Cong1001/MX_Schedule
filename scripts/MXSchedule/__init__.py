import sys

def CheckWindow(ssm, window_name):
    WindowCheck = ssm.describe_maintenance_windows(
        Filters=[
            {
                'Key': 'Name',
                'Values': [window_name]
            }
        ]
    )
    if WindowCheck['WindowIdentities'] == []:
        Window_ID = 'None'
    else:
        Window_ID = WindowCheck['WindowIdentities'][0]['WindowId']
    return Window_ID
    
def CreateWindow(ssm, window_name, cron):
    try:
        Window = ssm.create_maintenance_window(
            Name = window_name,
            Schedule = cron,
            Duration = 8,
            Cutoff = 0,
            AllowUnassociatedTargets = False
        )
        Window_ID = Window['WindowId']
        print("Created %s Maintenance Window successfully, id %s" %(window_name, Window_ID))
        return Window_ID
    except:
        print("Create %s Maintenance Window failed!" %window_name)
        e = sys.exc_info()[1]
        print("%s" %e)
        
def UpdateWindow(ssm, Window_ID, window_name, cron):
    try:
        ssm.update_maintenance_window(
            WindowId = Window_ID,
            Name = window_name,
            Schedule = cron,
            Duration=8,
            Cutoff=0,
            AllowUnassociatedTargets=False
        )
        print("Update %s Maintenance Window successfully, id %s" %(window_name, Window_ID))
    except:
        print("Update %s Maintenance Window failed! Window ID is %s" %(window_name, Window_ID))
        e = sys.exc_info()[1]
        print("%s" %e)
        
def CheckTarget(ssm, Window_ID, target_name):
    target_info = ssm.describe_maintenance_window_targets(
        WindowId = Window_ID
    )
    for target in target_info['Targets']:
        if target_name == target['Name']:
            target_ID = target['WindowTargetId']
            return target_ID
    target_ID = 'None'
    return target_ID
    
def RegisterTarget(ssm, Window_ID, target_name, Group_List):
    try:
        Target = ssm.register_target_with_maintenance_window(
            WindowId = Window_ID,
            ResourceType='INSTANCE',
            Targets=[
                {
                    'Key': 'tag:Patch Group',
                    'Values': Group_List
                }
            ],
            Name=target_name
        )
        Target_ID = Target['WindowTargetId']
        print("Register Maintenance Window %s Target successfully! MW_TARGET ID is %s" %(target_name, Target_ID))
        return Target_ID
    except:
        print("ERROR: Failed to register %s Target in Maintenance Window %s" %(target_name, Window_ID))
        e = sys.exc_info()[1]
        print("%s" %e)
        
def UpdateTarget(ssm, Window_ID, Target_ID, target_name, Group_List):
    try:
        ssm.update_maintenance_window_target(
            WindowId = Window_ID,
            WindowTargetId = Target_ID,
            Targets=[
                {
                    'Key': 'tag:Patch Group',
                    'Values': Group_List
                }
            ],
            Name=target_name
        )
        print("Maintenance Window %s Target already exist and updated! MW_TARGET ID is %s" %(target_name, Target_ID))
    except:
        print("Maintenance Window %s Target already exist but update failed! MW_TARGET ID is %s" %(target_name, Target_ID))
        e = sys.exc_info()[1]
        print("%s" %e)
        
def CheckTask(ssm, Window_ID, task_name):
    task_info = ssm.describe_maintenance_window_tasks(
        WindowId = Window_ID
    )
    for task in task_info['Tasks']:
        if task['Name'] == task_name:
            Task_ID = task['WindowTaskId']
            return Task_ID
    Task_ID = 'None'
    return Task_ID

def RegisterTask(ssm, Window_ID, task_name, mw_targets, s3_bucket, s3_folder):
    try:
        ssm.register_task_with_maintenance_window(
            Name = task_name,
            WindowId = Window_ID,
            Targets=[
                {
                    'Key': 'WindowTargetIds',
                    'Values': mw_targets
                }
            ],
            TaskArn='AWS-RunPatchBaseline',
            TaskType='RUN_COMMAND',
            MaxConcurrency='50',
            MaxErrors='50',
            Priority=1,
            TaskInvocationParameters={
                'RunCommand': {
                    'OutputS3BucketName': s3_bucket,
                    'OutputS3KeyPrefix': s3_folder,
                    'Parameters': {
                        'Operation': [
                            'Install'
                        ]
                    }
                }
            }
        )
        print("Register Install_Patch task with Maintenance Window %s successfully!" %Window_ID)
    except:
        print("Register Install_Patch task with Maintenance Window %s failed!" %Window_ID)
        e = sys.exc_info()[1]
        print("%s" %e)
        
def UpdateTask(ssm, Window_ID, Task_ID, task_name, mw_targets, s3_bucket, s3_folder):
    try:
        ssm.update_maintenance_window_task(
            WindowId = Window_ID,
            WindowTaskId = Task_ID,
            Name=task_name,
            Targets=[
                {
                    'Key': 'WindowTargetIds',
                    'Values': mw_targets
                }
            ],
            TaskArn='AWS-RunPatchBaseline',
            MaxConcurrency='50',
            MaxErrors='50',
            Priority=1,
            TaskInvocationParameters={
                'RunCommand': {
                    'OutputS3BucketName': s3_bucket,
                    'OutputS3KeyPrefix': s3_folder,
                    'Parameters': {
                        'Operation': [
                            'Install'
                        ]
                    }
                }
            }
        )
        print("Install_Patch task already exist and update successfully! MW_TASK ID is %s." %Task_ID)
    except:
        print("Install_Patch task already exist but update failed! MW_TASK ID is %s." %Task_ID)
        e=sys.exc_info()[1]
        print("%s" %e)

def RegisterLinuxRunCMD(ssm, Window_ID, task_name, mw_targets, s3_bucket, s3_folder, cmd):
    try:
        ssm.register_task_with_maintenance_window(
            Name = task_name,
            WindowId = Window_ID,
            Targets=[
                {
                    'Key': 'WindowTargetIds',
                    'Values': mw_targets
                }
            ],
            TaskArn='AWS-RunShellScript',
            TaskType='RUN_COMMAND',
            MaxConcurrency='50',
            MaxErrors='50',
            Priority=5,
            TaskInvocationParameters={
                'RunCommand': {
                    'OutputS3BucketName': s3_bucket,
                    'OutputS3KeyPrefix': s3_folder,
                    'Parameters': {
                        'commands': [
                            cmd
                        ]
                    }
                }
            }
        )
        print("Register Install_Patch task with Maintenance Window %s successfully!" %Window_ID)
    except:
        print("Register Install_Patch task with Maintenance Window %s failed!" %Window_ID)
        e = sys.exc_info()[1]
        print("%s" %e)

def UpdateLinuxRunCMD(ssm, Window_ID, Task_ID, task_name, mw_targets, s3_bucket, s3_folder, cmd):
    try:
        ssm.update_maintenance_window_task(
            WindowId = Window_ID,
            WindowTaskId = Task_ID,
            Name=task_name,
            Targets=[
                {
                    'Key': 'WindowTargetIds',
                    'Values': mw_targets
                }
            ],
            TaskArn='AWS-RunShellScript',
            MaxConcurrency='50',
            MaxErrors='50',
            Priority=5,
            TaskInvocationParameters={
                'RunCommand': {
                    'OutputS3BucketName': s3_bucket,
                    'OutputS3KeyPrefix': s3_folder,
                    'Parameters': {
                        'commands': [
                            cmd
                        ]
                    }
                }
            }
        )
        print("Install_Patch task already exist and update successfully! MW_TASK ID is %s." %Task_ID)
    except:
        print("Install_Patch task already exist but update failed! MW_TASK ID is %s." %Task_ID)
        e=sys.exc_info()[1]
        print("%s" %e)