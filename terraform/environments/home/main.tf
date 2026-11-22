module "media_network" {
  source = "../../modules/docker-network"

  name       = "homelab-media"
  driver     = "bridge"
  internal   = false
  attachable = true
}

module "monitoring_network" {
  source = "../../modules/docker-network"

  name       = "homelab-monitoring-v2"
  driver     = "bridge"
  internal   = false
  attachable = false
}