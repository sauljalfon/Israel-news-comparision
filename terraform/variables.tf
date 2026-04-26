variable "subscription_id" {
  description = "The subscription ID to deploy resources to."
  type        = string
  default     = "dab90331-d98b-4f31-a28e-b924fb330742"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "israel-news-comparision"
}

variable "short_project_name" {
  description = "The short name of the project."
  type        = string
  default     = "ilnewscomp"
}

variable "environment" {
  description = "The environment to deploy to (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "The Azure region to deploy resources to."
  type        = string
  default     = "israelcentral"
}

variable "tags" {
  description = "The tags to apply to the resources."
  type        = map(string)
  default = {
    project     = "israel-news-comparision"
    environment = "dev"
    managed_by  = "terraform"
  }
}

variable "synapse_sql_admin_user" {
  description = "The username for the Synapse SQL admin user."
  type        = string
  default     = "sqladmin"
}

variable "synapse_sql_admin_password" {
  description = "The password for the Synapse SQL admin user."
  type        = string
  sensitive   = true
}

variable "vm_admin_username" {
  description = "The username for the VM admin user."
  type        = string
  default     = "azureuser"
}

variable "ssh_key_path" {
  description = "The path to the SSH key for the VM."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "openai_api_key" {
  description = "The API key for OpenAI"
  type        = string
  sensitive   = true
}

