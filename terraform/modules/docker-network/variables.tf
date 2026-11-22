variable "name" {
  description = "Docker network name"
  type        = string
}

variable "driver" {
  description = "Docker network driver"
  type        = string
  default     = "bridge"
}

variable "attachable" {
  description = "Allow standalone containers to attach"
  type        = bool
  default     = false
}

variable "internal" {
  description = "Restrict external connectivity"
  type        = bool
  default     = false
}