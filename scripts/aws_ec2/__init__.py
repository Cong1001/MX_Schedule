def get_group_list(ec2, ssm):
    GROUP_LIST=[]
    InstanceList=ssm.describe_instance_information(
    	MaxResults=50
    )
    for Instance in InstanceList.get('InstanceInformationList'):
    	InstanceID=Instance.get('InstanceId')
    	tag_info=ec2.describe_tags(
    		Filters=[
    			{
    				'Name': 'key',
    				'Values': [
    					'Patch Group'
    				]
    			},
    			{
    				'Name': 'resource-id',
    				'Values': [
    					InstanceID
    				]
    			}
    		]
    	)
    	for tag in tag_info.get('Tags'):
    	    if ((tag.get('Value')).split('-'))[1] != 'non':
    		    GROUP_LIST.append(tag.get('Value'))
    GROUP_LIST=list(set(GROUP_LIST))
    while '' in GROUP_LIST:
        GROUP_LIST.remove('')
    return GROUP_LIST
    
def get_dev_group_list(group_list):
    dev_group_list=[]
    for group in group_list:
        if group[:3] == 'Win' or (group.split('-'))[1] != 'prd':
            dev_group_list.append(group)
    return dev_group_list
    
def get_prd_group_list(group_list):
    prd_group_list=[]
    for group in group_list:
        if group[:3] != 'Win' and (group.split('-'))[1] == 'prd':
            prd_group_list.append(group)
    return prd_group_list