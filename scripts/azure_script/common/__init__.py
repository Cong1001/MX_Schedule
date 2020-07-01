import sys
import OpenSSL, base64
from azure.mgmt.resource.resources.models import DeploymentMode

def send_command(compute_client, resource_group_name, vm_name, run_command_parameters):
    try:
        run_cmd = compute_client.virtual_machines.run_command(resource_group_name, vm_name, run_command_parameters)
        print("Send command to " + vm_name + " successfully!")
        return run_cmd
    except:
        e = sys.exc_info()[1]
        print(e)

def template_deploy(resource_client, resource_group_name, deployment_name, template, parameters):
    properties = {
        'mode': DeploymentMode.incremental,
        'template': template,
        'parameters': parameters
    }
    deployment_operation = resource_client.deployments.create_or_update(resource_group_name, deployment_name, properties)
    deployment_operation.wait()
    return deployment_operation

def generate_selfsign_cert_base64_value():
    key = OpenSSL.crypto.PKey() 
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048) 
    cert = OpenSSL.crypto.X509() 
    cert.set_serial_number(0) 
    cert.get_subject().CN = "me" 
    cert.set_issuer(cert.get_subject()) 
    cert.gmtime_adj_notBefore(0) 
    cert.gmtime_adj_notAfter(10*365*24*60*60) 
    cert.set_pubkey(key) 
    cert.sign(key, 'md5') 
    p12 = OpenSSL.crypto.PKCS12() 
    p12.set_privatekey(key) 
    p12.set_certificate(cert)
    base64_value = (base64.encodebytes(p12.export())).decode('utf-8')
    return base64_value

def generate_ws_aa_link_template():
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "omsWorkspaceName": {
                "type": "String",
                "metadata": {
                    "description": "OMS log analytics workspace name"
                }
            },
            "accountResourceId": {
                "type": "String",
                "metadata": {
                    "description": "Automation account resource id"
                }
            },
            "workspaceLocation": {
                "type": "String",
                "metadata": {
                    "description": "Automation account location"
                }
            }
        },
        "variables": {
            "apiVersion": {
                "oms": "2017-03-15-preview",
                "omssolutions": "2015-11-01-preview",
                "automation": "2015-10-31"
            },
            "updates": {
                "name": "[concat('Updates', '(', parameters('omsWorkspaceName'), ')')]",
                "galleryName": "Updates"
            }
        },
        "resources": [
            {
                "type": "Microsoft.OperationalInsights/workspaces/linkedServices",
                "apiVersion": "2015-11-01-preview",
                "name": "[concat(parameters('omsWorkspaceName'), '/' , 'Automation')]",
                "location": "[parameters('workspaceLocation')]",
                "properties": {
                    "resourceId": "[parameters('accountResourceId')]"
                }
            },
            {
                "type": "Microsoft.OperationsManagement/solutions",
                "apiVersion": "[variables('apiVersion').omssolutions]",
                "name": "[variables('updates').name]",
                "location": "[resourceGroup().location]",
                "plan": {
                    "name": "[variables('updates').name]",
                    "publisher": "Microsoft",
                    "promotionCode": "",
                    "product": "[concat('OMSGallery/', variables('updates').galleryName)]"
                },
                "properties": {
                    "workspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces/', parameters('omsWorkspaceName'))]"
                },
                "id": "[concat('/subscriptions/', subscription().subscriptionId, '/resourceGroups/', resourceGroup().name, '/providers/Microsoft.OperationsManagement/solutions/', variables('updates').name)]"
            }
        ]
    }
    return template