resource "aws_lambda_function" "main" {
  filename         = "${path.module}/../../deploy/lambda.zip"
  function_name    = var.function_name
  role             = aws_iam_role.lambda.arn
  handler          = var.handler
  runtime          = var.runtime
  memory_size      = 2048
  timeout          = 900
  
  environment {
    variables = var.environment
  }

  tracing_config {
    mode = "Active"
  }
}

resource "aws_iam_role" "lambda" {
  name = "${var.function_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}