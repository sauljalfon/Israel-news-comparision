resource "azurerm_cognitive_account" "openai" {
    name                = "oai-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = var.openai_location
    kind                = "OpenAI"
    sku_name            = "S0"
    custom_subdomain_name = "oai-${var.project_name}-${var.environment}"
    tags = var.tags
}

resource "azurerm_cognitive_deployment" "gpt4omini" {
    name = "gpt4omini"
    cognitive_account_id = azurerm_cognitive_account.openai.id

    model {
        format  = "OpenAI"
        name    = "gpt-4.1-mini"
        version = "2025-04-14"
    }

    sku {
        name = "Standard"
        capacity = 1
    }
}