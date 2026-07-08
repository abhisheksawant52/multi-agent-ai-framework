locals {
  name = "${var.name_prefix}-${var.environment}"
}

# Container registry for the agent worker image built from the Dockerfile.
resource "aws_ecr_repository" "agent_worker" {
  name                 = "${local.name}-worker"
  image_tag_mutability = var.ecr_image_tag_mutability
  force_delete         = var.environment != "prod"

  image_scanning_configuration {
    scan_on_push = var.ecr_scan_on_push
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = var.tags
}

# Keep only the most recent images to control storage cost.
resource "aws_ecr_lifecycle_policy" "agent_worker" {
  repository = aws_ecr_repository.agent_worker.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = { type = "expire" }
      }
    ]
  })
}

# Task queue that feeds work to agent workers, with a dead-letter queue.
module "agent_queue" {
  source = "./modules/agent_queue"

  name                       = "${local.name}-tasks"
  visibility_timeout_seconds = var.task_visibility_timeout_seconds
  max_receive_count          = var.task_max_receive_count
  tags                       = var.tags
}
