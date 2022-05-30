# Output value definitions

# output "lambda_bucket_name" {
#   description = "Name of the S3 bucket used to store function code."

#   value = aws_s3_bucket.lambda_bucket.id
# }

output "zip_md5" {
    description = "MD5 of lambda archive"
    value = filemd5(data.archive_file.lambda_query_handler.output_path)
}

output "data_reader_user" {
    description = "Reader User Key"
    value = "${aws_iam_access_key.data_reader.id} : ${aws_iam_access_key.data_reader.secret}"
    sensitive = true
}

output "data_writer_user" {
    description = "Writer User Key"
    value = "${aws_iam_access_key.data_writer.id} : ${aws_iam_access_key.data_writer.secret}"
    sensitive = true
}

output "api_uri" {
    description = "Webhook invocation uri"
    value = aws_apigatewayv2_stage.lambda.invoke_url
}

