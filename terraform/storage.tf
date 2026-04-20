resource "azurerm_storage_account" "main" {
    name = "st${var.short_project_name}${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    account_tier = "Standard"
    account_replication_type = "LRS"
    tags = var.tags
}

resource "azurerm_storage_container" "raw" {
    name = "raw"
    storage_account_id = azurerm_storage_account.main.id
    container_access_type = "private"
}

resource "azurerm_storage_container" "enriched" {
    name = "enriched"
    storage_account_id = azurerm_storage_account.main.id
    container_access_type = "private"
  
}

resource "azurerm_storage_container" "processed" {
    name = "processed"
    storage_account_id = azurerm_storage_account.main.id
    container_access_type = "private"
}

resource "azurerm_storage_container" "reports" {
    name = "reports"
    storage_account_id = azurerm_storage_account.main.id
    container_access_type = "private"  
}