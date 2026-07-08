variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, prod)."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, or prod."
  }
}

variable "name_prefix" {
  description = "Prefix applied to created resource names."
  type        = string
  default     = "multi-agent"
}

variable "ecr_image_tag_mutability" {
  description = "Whether ECR image tags are MUTABLE or IMMUTABLE."
  type        = string
  default     = "IMMUTABLE"
}

variable "ecr_scan_on_push" {
  description = "Enable image vulnerability scanning on push."
  type        = bool
  default     = true
}

variable "task_visibility_timeout_seconds" {
  description = "SQS visibility timeout for agent task messages."
  type        = number
  default     = 300
}

variable "task_max_receive_count" {
  description = "Deliveries before a message is moved to the dead-letter queue."
  type        = number
  default     = 5
}

variable "tags" {
  description = "Additional tags merged onto all resources."
  type        = map(string)
  default     = {}
}
