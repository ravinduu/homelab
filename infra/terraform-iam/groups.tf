resource "aws_iam_group" "developers" {
  name = "LabDevelopers"
}

resource "aws_iam_group" "auditors" {
  name = "LabAuditors"
}

resource "aws_iam_user_group_membership" "alice" {
  user = aws_iam_user.users["lab-alice"].name

  groups = [
    aws_iam_group.developers.name,
    aws_iam_group.auditors.name
  ]
}

resource "aws_iam_user_group_membership" "bob" {
  user = aws_iam_user.users["lab-bob"].name

  groups = [
    aws_iam_group.auditors.name
  ]
}