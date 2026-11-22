output "id" {
  description = "Docker network ID"
  value       = docker_network.this.id
}

output "name" {
  description = "Docker network name"
  value       = docker_network.this.name
}