locals {
  users = toset([
    "lab-alice",
    "lab-bob"
  ])
}

resource "aws_iam_user" "users" {
  for_each = local.users

  name = each.value

  tags = {
    Environment = "lab"
    ManagedBy   = "terraform"
  }
}