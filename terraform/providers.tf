provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "multi-agent-ai-framework"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
