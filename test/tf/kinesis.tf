provider "aws" {
  region                  = var.region
  profile                 = var.profile
}


locals {
  group = flatten([
    for name in keys(var.log) : [
      for loggroup in var.log[name] : {
        name   = name
        loggroup = loggroup
      }
    ]
  ])
  name = { for entry in local.group: "${entry.name}.${entry.loggroup}" => entry }
}



module "kinesis_firehose" {
  source = "refer/disney/github/module"
  for_each    = local.name
  region = var.region
  name_cloudwatch_logs_to_ship = each.value.loggroup
  kinesis_name = each.value.name
  account_num = var.account_num
  hec_token = var.hec_token
  hec_url = var.hec_url
  s3_bucket_name_prefix = var.s3_bucket_name_prefix
}
