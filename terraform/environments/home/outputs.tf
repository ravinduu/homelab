output "media_network_id" {
  description = "Media Docker network ID"
  value       = module.media_network.id
}

output "monitoring_network_id" {
  description = "Monitoring Docker network ID"
  value       = module.monitoring_network.id
}