data "aws_iam_policy_document" "s3_read_only" {
  statement {
    sid    = "ListLabBucket"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::iam-security-lab-701837200616-us-east-1-an"
    ]
  }

  statement {
    sid    = "ReadLabObjects"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::iam-security-lab-701837200616-us-east-1-an/*"
    ]
  }
}

resource "aws_iam_policy" "s3_read_only" {
  name        = "LabTerraformS3ReadOnly"
  description = "Read-only access to the IAM lab S3 bucket"

  policy = data.aws_iam_policy_document.s3_read_only.json
}

resource "aws_iam_group_policy_attachment" "developers" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.s3_read_only.arn
}

resource "aws_iam_group_policy_attachment" "auditors" {
  group      = aws_iam_group.auditors.name
  policy_arn = aws_iam_policy.s3_read_only.arn
}