#!/usr/bin/env python3.6

import os
from settings import GetSettings

if __name__ == '__main__':
    settings = GetSettings()
    if settings.Cloud == 'AWS':
        if settings.SingleCustomer == 'false':
            os.system("python3.6 ./scripts/AWS_MX_Schedule_Region.py")
        else:
            os.system("python3.6 ./scripts/AWS_MX_Schedule.py")
    elif settings.Cloud == 'Azure':
        os.system("python3.6 ./scripts/azure_script/Azure_MX_Schedule.py")
    else:
        print("Unknow Cloud Platform!")
