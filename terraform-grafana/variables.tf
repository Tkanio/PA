variable "grafana_url" {
  description = "URL Grafana"
  type        = string
}

variable "grafana_api_key" {
  description = "Token API Grafana (Service Account avec droits Admin ou Editor)"
  type        = string
  sensitive   = true
}

variable "prometheus_datasource_name" {
  description = "Nom exact de la datasource Prometheus dans Grafana"
  type        = string
}