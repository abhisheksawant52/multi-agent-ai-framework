output "ecr_repository_url" {
  description = "URL of the agent worker container repository."
  value       = aws_ecr_repository.agent_worker.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the agent worker container repository."
  value       = aws_ecr_repository.agent_worker.arn
}

output "task_queue_url" {
  description = "URL of the agent task SQS queue."
  value       = module.agent_queue.queue_url
}

output "task_queue_arn" {
  description = "ARN of the agent task SQS queue."
  value       = module.agent_queue.queue_arn
}

output "task_dlq_url" {
  description = "URL of the dead-letter queue."
  value       = module.agent_queue.dlq_url
}
