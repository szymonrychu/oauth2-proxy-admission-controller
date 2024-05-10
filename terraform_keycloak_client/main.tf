locals {
  root_url = "https://${var.keycloak_client_hostname}"
  valid_redirect_url = "https://${var.keycloak_client_hostname}/oauth2/callback"
}

resource "keycloak_openid_client" "this" {
  realm_id    = data.keycloak_realm.master.id
  access_type = "CONFIDENTIAL"
  login_theme = "keycloak"

  name          = var.keycloak_client_name != null ? var.keycloak_client_name : var.keycloak_client_id
  client_id     = var.keycloak_client_id
  client_secret = var.keycloak_client_secret

  enabled                      = true
  standard_flow_enabled        = true
  implicit_flow_enabled        = false
  direct_access_grants_enabled = true

  root_url  = local.root_url
  admin_url = local.root_url
  base_url  = local.root_url
  valid_redirect_uris = [
    local.valid_redirect_url
  ]
}

resource "keycloak_openid_audience_protocol_mapper" "this" {
  realm_id  = data.keycloak_realm.master.id
  client_id = keycloak_openid_client.this.id
  name      = "aud"

  included_client_audience = var.keycloak_client_id
}

resource "keycloak_openid_client_default_scopes" "this" {
  realm_id  = data.keycloak_realm.master.id
  client_id = keycloak_openid_client.this.id
  default_scopes = [
    "profile",
    "email",
    var.keycloak_openid_client_scope_name,
  ]
}

resource "keycloak_group" "this" {
  realm_id = data.keycloak_realm.master.id
  name     = var.keycloak_group_name != null ? var.keycloak_group_name : var.keycloak_client_id
}

resource "kubernetes_secret" "this" {
  metadata {
    name = var.kubernetes_secret_name != null ? var.kubernetes_secret_name : "${var.keycloak_client_id}-proxy"
    namespace = var.kubernetes_secret_namespace
  }
  data = {
    "proxy-cookie-domain": var.keycloak_client_hostname
    "proxy-allowed-groups": keycloak_group.this.name
    "proxy-client-id": keycloak_openid_client.this.client_id
    "proxy-client-secret": keycloak_openid_client.this.client_secret
    "proxy-cookie-secret": var.kuberenetes_proxy_cookie_secret
    "proxy-redirect-url": local.valid_redirect_url
  }
}
