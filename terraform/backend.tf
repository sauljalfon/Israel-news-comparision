terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
        source = "hashicorp/azurerm"
        version = "~> 4.0"
    }
  }

  backend "azurerm" {
    resource_group_name = "rg-tfstate-il-news-state-tfstate"
    storage_account_name = "sttfstateilnews"
    container_name = "tfstate"
    key = "terraform.tfstate"
  }
}