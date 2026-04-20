resource "azurerm_virtual_network" "main" {
    name = "vnet-${var.project_name}-${var.environment}"
    address_space = ["10.0.0.0/16"]
    location = azurerm_resource_group.main.location
    resource_group_name = azurerm_resource_group.main.name
    tags = var.tags
}

resource "azurerm_subnet" "main" {
    name = "snet-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    virtual_network_name = azurerm_virtual_network.main.name
    address_prefixes = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "vm" {
    name = "pip-vm-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    allocation_method = "Static"
    tags = var.tags  
}

resource "azurerm_network_security_group" "vm" {
    name = "nsg-vm-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    tags = var.tags

    security_rule {
        name                       = "AllowSSH"
        priority                   = 1001
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }

    security_rule {
        name                       = "AllowAirflow"
        priority                   = 1002
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "8080"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
}

resource "azurerm_network_interface" "vm" {
    name = "nic-vm-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    tags = var.tags

    ip_configuration {
        name                          = "internal"
        subnet_id                     = azurerm_subnet.main.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.vm.id
    }
}

resource "azurerm_network_interface_security_group_association" "vm" {
    network_interface_id      = azurerm_network_interface.vm.id
    network_security_group_id = azurerm_network_security_group.vm.id
}

resource "azurerm_linux_virtual_machine" "airflow" {
    name = "vm-airflow-${var.project_name}-${var.environment}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    size = "Standard_B2s_v2"
    admin_username = var.vm_admin_username
    tags = var.tags

    network_interface_ids = [
        azurerm_network_interface.vm.id
    ]

    admin_ssh_key {
      username = var.vm_admin_username
      public_key = file(var.ssh_key_path)
    }

    os_disk {
        caching              = "ReadWrite"
        storage_account_type = "Standard_LRS"
        disk_size_gb = 30
    }

    source_image_reference {
        publisher = "Canonical"
        offer     = "ubuntu-24_04-lts"
        sku       = "server"
        version   = "latest"
    } 

    disable_password_authentication = true
}