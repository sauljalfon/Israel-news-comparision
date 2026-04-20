resource "azurerm_storage_account" "synapse" {
    name                        = "st${var.short_project_name}syn${var.environment}"
    resource_group_name         = azurerm_resource_group.main.name
    location                    = azurerm_resource_group.main.location
    account_tier                = "Standard"
    account_replication_type    = "LRS"
    account_kind                = "StorageV2"
    is_hns_enabled              = true
    tags                        = var.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
    name              = "synapse"
    storage_account_id = azurerm_storage_account.synapse.id  
}

resource "azurerm_synapse_workspace" "main" {
    name = "syn-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse.id
    sql_administrator_login = var.synapse_sql_admin_user
    sql_administrator_login_password = var.synapse_sql_admin_password
    tags = var.tags

    identity {
      type = "SystemAssigned"
    }
}

resource "azurerm_synapse_firewall_rule" "allow_all" {
    name = "AllowAll"
    synapse_workspace_id = azurerm_synapse_workspace.main.id
    start_ip_address = "0.0.0.0"
    end_ip_address = "255.255.255.255"
}

resource "azurerm_role_assignment" "synapse_blob_reader" {
    scope = azurerm_storage_account.main.id
    role_definition_name = "Storage Blob Data Reader"
    principal_id = azurerm_synapse_workspace.main.identity[0].principal_id  
}

resource "azurerm_role_assignment" "synapse_adls_contributor" {
    scope = azurerm_storage_account.synapse.id
    role_definition_name = "Storage Blob Data Contributor"
    principal_id = azurerm_synapse_workspace.main.identity[0].principal_id  
}