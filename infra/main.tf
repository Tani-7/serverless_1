terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "lambda_processor" {
  source          = "./modules/lambda"
  function_name   = "csv-parallel-processor"
  handler         = "lambda_processor.handler"
  runtime         = "python3.9"
  environment     = {
    PROCESSED_BUCKET = aws_s3_bucket.processed.bucket
    MAX_WORKERS      = 20
  }
}

module "monitoring" {
  source        = "./modules/monitoring"
  lambda_arn    = module.lambda_processor.function_arn
  s3_bucket_arn = aws_s3_bucket.raw.arn
}