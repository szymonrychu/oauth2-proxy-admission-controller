variable "keycloak_url" {
  description = "Keycloak url"
  type        = string
  nullable    = false
}

variable "keycloak_client_name" {
  description = "Name of the client in keycloak"
  type        = string
  nullable    = true
}

variable "keycloak_client_id" {
  description = "Id of the client in keycloak"
  sensitive   = true
  type        = string
  nullable    = false
}

variable "keycloak_client_secret" {
  description = "Secret of the client in keycloak"
  default     = null
  sensitive   = true
  type        = string
  nullable    = true
}

variable "keycloak_client_hostname" {
  description = "Hostname of the OIDC client"
  type        = string
  nullable    = false
}

variable "keycloak_group_name" {
  description = "Name of the keyloak group name"
  type        = string
  nullable    = true
}

variable "keycloak_openid_client_scope_name" {
  description = "Name of the groups openid scope"
  type        = string
  nullable    = false
}

variable "kuberenetes_proxy_cookie_secret" { # o8NhPX6KJIqo1GXE
  description = "Cookie secret for the oauth2proxy"
  sensitive   = true
  type        = string
  nullable    = false
}

variable "kubernetes_secret_name" {
  description = "Name of the kubernetes secret"
  default     = null
  type        = string
  nullable    = true
}

variable "kubernetes_secret_namespace" {
  description = "Namespace of the kubernetes secret"
  default     = null
  type        = string
  nullable    = true
}

