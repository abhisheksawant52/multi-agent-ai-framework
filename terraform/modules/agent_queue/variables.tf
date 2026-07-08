variable "name" {
  description = "Base name for the queue and its dead-letter queue."
  type        = string
}

variable "visibility_timeout_seconds" {
  description = "Time a message stays invisible after being received."
  type        = number
  default     = 300
}

variable "message_retention_seconds" {
  description = "How long messages are retained in the main queue."
  type        = number
  default     = 345600
}

variable "max_receive_count" {
  description = "Receives before a message is routed to the dead-letter queue."
  type        = number
  default     = 5
}

variable "tags" {
  description = "Tags applied to the queues."
  type        = map(string)
  default     = {}
}
