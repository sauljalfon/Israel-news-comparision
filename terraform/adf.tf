resource "azurerm_data_factory" "main" {
    name               = "adf-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location            = azurerm_resource_group.main.location
    tags                = var.tags

    identity {
      type = "SystemAssigned"
    }
}

resource "azurerm_role_assignment" "adf_blob_contributor" {
    scope                = azurerm_storage_account.main.id
    role_definition_name = "Storage Blob Data Contributor"
    principal_id         = azurerm_data_factory.main.identity[0].principal_id
  
}