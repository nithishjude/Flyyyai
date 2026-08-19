# =============================================================================
# infrastructure.tf — Testbed: support-portal cloud infrastructure
#
# This file represents the Terraform configuration for the AI components of
# the support-portal application. It declares an Azure OpenAI deployment.
#
# Purpose for the scanner:
#   The discovery system should detect the `azurerm_cognitive_account` and
#   `azurerm_cognitive_deployment` resource types and associate them with
#   the Azure OpenAI provider. The model name ("gpt-4o-mini") should be
#   extracted as a MODEL_NAME_STRING evidence record.
# =============================================================================

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource group for all support-portal cloud resources
resource "azurerm_resource_group" "support_portal_rg" {
  name     = "support-portal-rg"
  location = "East US"
}

# Azure OpenAI Cognitive Services account
resource "azurerm_cognitive_account" "openai_account" {
  name                = "support-portal-openai"
  location            = azurerm_resource_group.support_portal_rg.location
  resource_group_name = azurerm_resource_group.support_portal_rg.name
  kind                = "OpenAI"
  sku_name            = "S0"

  tags = {
    application = "support-portal"
    purpose     = "customer-support-llm"
    environment = "production"
  }
}

# Azure OpenAI model deployment — GPT-4o-mini for customer support responses
resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = "gpt-4o-mini-deployment"
  cognitive_account_id = azurerm_cognitive_account.openai_account.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }

  scale {
    type     = "Standard"
    capacity = 10
  }
}

# Application config — injects AZURE_OPENAI_API_KEY into app container
resource "azurerm_container_app_environment" "support_portal_env" {
  name                       = "support-portal-env"
  location                   = azurerm_resource_group.support_portal_rg.location
  resource_group_name        = azurerm_resource_group.support_portal_rg.name
}

# Outputs for reference by the application
output "azure_openai_endpoint" {
  value     = azurerm_cognitive_account.openai_account.endpoint
  sensitive = false
}

output "azure_openai_model" {
  value = "gpt-4o-mini"
}
