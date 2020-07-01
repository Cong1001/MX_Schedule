import sys

def CheckBaseline(ssm, group):
    Baseline=ssm.describe_patch_baselines(
        Filters=[
            {
                'Key': 'NAME_PREFIX',
                'Values': [group]
            }
        ]
    )
    if Baseline['BaselineIdentities'] == []:
        BaselineID='None'
    else:
        BaselineID=Baseline['BaselineIdentities'][0]['BaselineId']
    return BaselineID
    
def CreateLinuxBaseline(ssm, OS, group, product, severity, classification, rejectpatches):
    try:
        Baseline = ssm.create_patch_baseline(
            OperatingSystem=OS,
            Name=group,
            ApprovalRules={
                'PatchRules': [
                    {
                        'PatchFilterGroup': {
                            'PatchFilters': [
                                {
                                    'Key': 'PRODUCT',
                                    'Values': product
                                },
                                {
                                    'Key': 'CLASSIFICATION',
                                    'Values': classification
                                },
                                {
                                    'Key': 'SEVERITY',
                                    'Values': severity
                                }
                            ]
                        },
                        'ApproveAfterDays': 0,
                        'EnableNonSecurity': True
                    }
                ]
            },
            ApprovedPatchesEnableNonSecurity=True,
            RejectedPatches=rejectpatches,
            RejectedPatchesAction='BLOCK'
        )
        print("Create %s Baseline Successfully!" %group)
        BaselineID = Baseline['BaselineId']
        return BaselineID
    except:
        print("Create %s Baseline Failed!" %group)
        e=sys.exc_info()[1]
        print("%s" %e)
        
def CreateWindowsBaseline(ssm, OS, group, product, severity, classification, rejectpatches):
    try:
        Baseline = ssm.create_patch_baseline(
            OperatingSystem=OS,
            Name=group,
            ApprovalRules={
                'PatchRules': [
                    {
                        'PatchFilterGroup': {
                            'PatchFilters': [
                                {
                                    'Key': 'PRODUCT',
                                    'Values': product
                                },
                                {
                                    'Key': 'CLASSIFICATION',
                                    'Values': classification
                                },
                                {
                                    'Key': 'MSRC_SEVERITY',
                                    'Values': severity
                                }
                            ]
                        },
                        'ApproveAfterDays': 0
                    }
                ]
            },
            RejectedPatches=rejectpatches,
            RejectedPatchesAction='BLOCK'
        )
        print("Create %s Baseline Successfully!" %group)
        BaselineID = Baseline['BaselineId']
        return BaselineID
    except:
        print("Create %s Baseline Failed!" %group)
        e=sys.exc_info()[1]
        print("%s" %e)
        
def UpdateLinuxBaseline(ssm, BaselineID, group, product, severity, classification, rejectpatches):
    try:
        Baseline = ssm.update_patch_baseline(
            BaselineId=BaselineID,
            Name=group,
            ApprovalRules={
                'PatchRules': [
                    {
                        'PatchFilterGroup': {
                            'PatchFilters': [
                                {
                                    'Key': 'PRODUCT',
                                    'Values': product
                                },
                                {
                                    'Key': 'CLASSIFICATION',
                                    'Values': classification
                                },
                                {
                                    'Key': 'SEVERITY',
                                    'Values': severity
                                }
                            ]
                        },
                        'ApproveAfterDays': 0,
                        'EnableNonSecurity': True
                    }
                ]
            },
            ApprovedPatchesEnableNonSecurity=True,
            RejectedPatches=rejectpatches,
            RejectedPatchesAction='BLOCK'
        )
        print("Update %s Baseline %s Successfully!" %(group, BaselineID))
    except:
        print("Update %s Baseline %s Failed!" %(group, BaselineID))
        e=sys.exc_info()[1]
        print("%s" %e)
        
def UpdateWindowsBaseline(ssm, BaselineID, group, product, severity, classification, rejectpatches):
    try:
        Baseline = ssm.update_patch_baseline(
            BaselineId=BaselineID,
            Name=group,
            ApprovalRules={
                'PatchRules': [
                    {
                        'PatchFilterGroup': {
                            'PatchFilters': [
                                {
                                    'Key': 'PRODUCT',
                                    'Values': product
                                },
                                {
                                    'Key': 'CLASSIFICATION',
                                    'Values': classification
                                },
                                {
                                    'Key': 'MSRC_SEVERITY',
                                    'Values': severity
                                }
                            ]
                        },
                        'ApproveAfterDays': 0
                    }
                ]
            },
            RejectedPatches=rejectpatches,
            RejectedPatchesAction='BLOCK'
        )
        print("Update %s Baseline %s Successfully!" %(group, BaselineID))
    except:
        print("Update %s Baseline %s Failed!" %(group, BaselineID))
        e=sys.exc_info()[1]
        print("%s" %e)
        
def RegisterBaselineForPatchGroup(ssm, BaselineID, group):
    try:
        ssm.register_patch_baseline_for_patch_group(
            BaselineId = BaselineID,
            PatchGroup = group
        )
        print("Register %s into %s successfully!" %(group, BaselineID))
    except:
        print("ERROR: Failed to register %s into %s" %(group, BaselineID))
        e=sys.exc_info()[1]
        print("%s" %e)
