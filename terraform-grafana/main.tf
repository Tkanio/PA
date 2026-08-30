terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.0"
    }
  }
}

provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_api_key
}

data "grafana_data_source" "prometheus" {
  name = var.prometheus_datasource_name
}

resource "grafana_folder" "monitoring" {
  title = "Monitoring Infra"
}

resource "grafana_dashboard" "titannium" {
  folder    = grafana_folder.monitoring.id
  overwrite = true
  config_json = templatefile("${path.module}/dashboards/titannium.json", {
    datasource_uid = data.grafana_data_source.prometheus.uid
  })
}

resource "grafana_folder" "ubika" {
  title = "UBIKA"
}

resource "grafana_dashboard" "ubika_waap" {
  folder      = grafana_folder.ubika.id
  config_json = templatefile("${path.module}/dashboards/ubika_dashboard.json", {
    datasource_uid = data.grafana_data_source.prometheus.uid
  })
  overwrite = true
}

output "prometheus_datasource_uid" {
  value = data.grafana_data_source.prometheus.uid
}