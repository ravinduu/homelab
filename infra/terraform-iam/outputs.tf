output "iam_users" {
  value = [
    for user in aws_iam_user.users : user.name
  ]
}

output "iam_groups" {
  value = [
    aws_iam_group.developers.name,
    aws_iam_group.auditors.name
  ]
}

output "s3_policy_arn" {
  value = aws_iam_policy.s3_read_only.arn
}