def get_vm_excludes_dict(run_ps_cmd_dict):
    vm_excludes_dict = {}
    for sub in run_ps_cmd_dict.keys():
        sub_excludes_dict = {}
        for vm in run_ps_cmd_dict[sub].keys():
            if run_ps_cmd_dict[sub][vm]['ps_command'].status() == 'Succeeded':
                for value in run_ps_cmd_dict[sub][vm]['ps_command'].result().as_dict()['value']:
                    if value['code'] == 'ComponentStatus/StdOut/succeeded':
                        KB_list = value['message'].split('\n')
                        sub_excludes_dict[vm] = {'vm_name': vm, 'Resource Group': run_ps_cmd_dict[sub][vm]['Resource Group'], 'Patch Group': run_ps_cmd_dict[sub][vm]['Patch Group'], 'excludes': KB_list}
        vm_excludes_dict[sub] = sub_excludes_dict
    return vm_excludes_dict

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

def add_addition_KBs(win_init_excludes_dict, excludes_KBs_dict):
    for sub in win_init_excludes_dict.keys():
        for vm in win_init_excludes_dict[sub].keys():
            win_type = (win_init_excludes_dict[sub][vm]['Patch Group'].split('-'))[0]
            if win_type in excludes_KBs_dict.keys():
                for KB in excludes_KBs_dict[win_type].keys():
                    if KB not in win_init_excludes_dict[sub][vm]['excludes']:
                        win_init_excludes_dict[sub][vm]['excludes'].append(KB)
    return win_init_excludes_dict