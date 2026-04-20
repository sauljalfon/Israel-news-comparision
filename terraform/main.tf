provider "azurerm" {
    features {}
    subscription_id = var.subscription_id
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "main" {
    name = "rg-${var.project_name}-${var.environment}"
    location = var.location
    tags = var.tags
}