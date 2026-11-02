terraform {
  required_providers {
    keycloak = {
      source  = "keycloak/keycloak"
      version = ">=5.0.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">=2.30.0"
    }
  }
}
