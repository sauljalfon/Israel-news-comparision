output "resource_group_name" {
    value = azurerm_resource_group.main.name  
}

output "storage_account_name" {
    value = azurerm_storage_account.main.name  
}

output "storage_account_key" {
    value = azurerm_storage_account.main.primary_access_key    
    sensitive = true
}

output "data_factory_name" {
    value = azurerm_data_factory.main.name
}

output "synapse_workspace_name" {
    value = azurerm_synapse_workspace.main.name
}

output "synapse_sql_endpoint" {
    value = azurerm_synapse_workspace.main.connectivity_endpoints["sql"]
}

output "openai_key" {
    value = azurerm_cognitive_account.openai.primary_access_key
    sensitive = true  
}

output "container_instance_ip" {
    value = azurerm_container_group.microservice.ip_address  
}

output "vmn_public_ip" {
    value = azurerm_public_ip.vm.ip_address  
}

output "vm_ssh_command" {
    value = "ssh ${var.vm_admin_username}@${azurerm_public_ip.vm.ip_address}"
}


