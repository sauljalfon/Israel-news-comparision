resource "azurerm_container_group" "microservice" {
    name                    = "aci-${var.project_name}-${var.environment}"
    resource_group_name     = azurerm_resource_group.main.name
    location                = azurerm_resource_group.main.location
    os_type                 = "Linux"
    ip_address_type         = "Public"
    tags                    = var.tags

    container {
      name      = "${var.project_name}-api"
      image     = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
      cpu       = 0.5
      memory    = 0.5

      ports {
        port = 8000
        protocol = "TCP"
      }

      environment_variables = {
        "AZURE_STORAGE_ACCOUNT_NAME"    = azurerm_storage_account.main.name
        "AZURE_OPENAI_ENDPOINT"         = azurerm_cognitive_account.openai.endpoint
      }

      secure_environment_variables = {
        "AZURE_STORAGE_ACCOUNT_KEY"     = azurerm_storage_account.main.primary_access_key
        "AZURE_OPENAI_KEY"              = azurerm_cognitive_account.openai.primary_access_key
      }
    }
}