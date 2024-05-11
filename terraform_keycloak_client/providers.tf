terraform {
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = ">=4.3.1"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">=2.30.0"
    }
  }
}
