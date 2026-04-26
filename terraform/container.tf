resource "azurerm_subnet" "containers" {
  name                 = "snet-acr-${var.project_name}-${var.environment}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "aci-delegation"
    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }

}


resource "azurerm_container_group" "microservices" {
  name                = "aci-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  ip_address_type     = "Private"
  subnet_ids          = [azurerm_subnet.containers.id]
  tags                = var.tags

  image_registry_credential {
    server   = azurerm_container_registry.microservices.login_server
    username = azurerm_container_registry.microservices.admin_username
    password = azurerm_container_registry.microservices.admin_password
  }

  container {
    name   = "extractor-news"
    image  = "${azurerm_container_registry.microservices.login_server}/extractor-news:latest"
    cpu    = 0.5
    memory = 0.5
    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      "PORT" = "8000"
    }
    secure_environment_variables = {
      "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
    }
  }

  container {
    name   = "extractor-market"
    image  = "${azurerm_container_registry.microservices.login_server}/extractor-market:latest"
    cpu    = 0.5
    memory = 0.5
    ports {
      port     = 8001
      protocol = "TCP"
    }
    environment_variables = {
      "PORT" = "8001"
    }
    secure_environment_variables = {
      "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
    }
  }

  container {
    name   = "enrich"
    image  = "${azurerm_container_registry.microservices.login_server}/enrich:latest"
    cpu    = 0.5
    memory = 0.5
    ports {
      port     = 8002
      protocol = "TCP"
    }
    environment_variables = {
      "PORT" = "8002"
    }
    secure_environment_variables = {
      "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
      "OPENAI_API_KEY"                  = var.openai_api_key
    }
  }

  container {
    name   = "transform"
    image  = "${azurerm_container_registry.microservices.login_server}/transform:latest"
    cpu    = 0.5
    memory = 0.5
    ports {
      port     = 8003
      protocol = "TCP"
    }

    environment_variables = {
      "PORT" = "8003"
    }

    secure_environment_variables = {
      "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
    }
  }

  container {
    name   = "synthesis"
    image  = "${azurerm_container_registry.microservices.login_server}/synthesis:latest"
    cpu    = 0.5
    memory = 0.5
    ports {
      port     = 8004
      protocol = "TCP"
    }

    environment_variables = {
      "PORT" = "8004"
    }

    secure_environment_variables = {
      "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
      "OPENAI_API_KEY"                  = var.openai_api_key
    }
  }
}

resource "azurerm_container_registry" "microservices" {
  name                = "acrilnewscompdev"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}
