output "kubernetes_secret_metadata" {
  value = kubernetes_secret.this.metadata
}

output "client_id" {
  description = "client id"
  value       = keycloak_openid_client.this.client_id
  sensitive   = true
}

output "client_secret" {
  description = "client secret"
  value       = keycloak_openid_client.this.client_secret
  sensitive   = true
}

output "cookie_secret" {
  description = "client secret"
  value       = var.kuberenetes_proxy_cookie_secret
  sensitive   = true
}

output "keycloak_group_name" {
  description = "keycloak group name"
  value       = keycloak_group.this.name
}

output "keycloak_group_id" {
  description = "keycloak group id"
  value       = keycloak_group.this.id
}