terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }

  backend "s3" {
    bucket = "invenerateterraformstate"
    key    = "radio_assistant/query_handler/terraform_state"
    region = "us-east-2"
    profile = "radio_assistant_admin"
  }

  required_version = "~> 1.0"
}

data "aws_canonical_user_id" "current" {}

provider "aws" {
  region = var.aws_region
  profile = "radio_assistant_admin"
}

## Groups and Users

### Exec Role

resource "random_pet" "lambda_exec_role_name" {
  prefix = "radio-assitant-exec"
  length = "2"
}

resource "aws_iam_role" "lambda_exec" {
  name = random_pet.lambda_exec_role_name.id

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

### Data Reader Name

resource "random_pet" "data_reader_name" {
  prefix = "radio-assitant-reader"
  length = "2"
}

resource "aws_iam_user" "data_reader" {
  name = random_pet.data_reader_name.id
}

resource "aws_iam_access_key" "data_reader" {
  user = aws_iam_user.data_reader.name
}

### Data Writer User

resource "random_pet" "data_writer_name" {
  prefix = "radio-assitant-writer"
  length = "2"
}

resource "aws_iam_user" "data_writer" {
  name = random_pet.data_writer_name.id
}

resource "aws_iam_access_key" "data_writer" {
  user = aws_iam_user.data_writer.name
}

## S3 Buckets

resource "random_pet" "lambda_bucket_name" {
  prefix = "radio-assitant-lambda"
  length = "2"
}

resource "random_pet" "data_bucket_name" {
  prefix = "radio-assitant-data"
  length = "2"
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = random_pet.lambda_bucket_name.id

  force_destroy = true
}

resource "aws_s3_bucket_acl" "lambda_private_acl" {
  bucket = aws_s3_bucket.lambda_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = random_pet.data_bucket_name.id

  force_destroy = true
}

resource "aws_s3_bucket_acl" "data_private_acl" {
  bucket = aws_s3_bucket.data_bucket.id
  acl    = "private"
}

data "aws_iam_policy_document" "data_bucket_policy" {
  statement {
    sid = "1"
    principals {
      type        = "AWS"
      identifiers = [
        aws_iam_user.data_reader.arn,
        aws_iam_user.data_writer.arn,
        aws_iam_role.lambda_exec.arn
        ]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [ "${aws_s3_bucket.data_bucket.arn}/*" ]
  }

  statement {
    sid = "2"

    principals {
      type        = "AWS"
      identifiers = [
        aws_iam_user.data_writer.arn,
        ]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [ "${aws_s3_bucket.data_bucket.arn}/*" ]
  }
}

resource "aws_s3_bucket_policy" "data_bucket_policy" {
  bucket = aws_s3_bucket.data_bucket.id
  policy = data.aws_iam_policy_document.data_bucket_policy.json
}

## Lambda Programming

# data "archive_file" "lambda_query_handler" {
#   type = "zip"

#   source_dir = "${path.module}/lambda"
#   output_path = "${path.module}/lambda.zip"
# }

locals {
  # Common tags to be assigned to all resources
  lambda_archive_path = abspath("${path.module}/lambda.zip")
}

resource "aws_s3_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "lambda.zip"
  source = "${path.module}/lambda.zip"

  etag = filemd5(local.lambda_archive_path )
}

resource "aws_lambda_function" "lambda_function" {
  function_name = "RadioAssistantRequestHandler"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_code.key

  runtime = "python3.9"
  handler = "main.main"

  timeout = 5

  source_code_hash = filebase64sha256(local.lambda_archive_path)

  role = aws_iam_role.lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "lambda_function" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"

  retention_in_days = 14
}

## API Gateway

resource "aws_apigatewayv2_api" "lambda" {
  name          = "radio_assistant_gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "webhook_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "lambda_function" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.lambda_function.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "lambda_post_route" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "POST /handler"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_function.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"

  retention_in_days = 14
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}