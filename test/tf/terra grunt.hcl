# DO NOT CHANGE THIS LOCALLY JUST TO RUN YOUR APPLY AS A TEST
# Running against the shared state permanent updates the shared state,
# and makes rolling back nearly impossible.

terraform_version_constraint = "0.13.2"

remote_state {
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  backend = "gcs/aws"
  config = {
    bucket  = "bucketname"
    prefix  = "${local.state_bucket_root}/${local.this_project}/state"
  }
}

locals {
  state_bucket_root = "splunk"
  this_project      = path_relative_to_include()
  repo_root         = path_relative_from_include()
}

inputs = {
  state_bucket_root = local.state_bucket_root
  this_project      = local.this_project
  repo_root         = local.repo_root
}

generate "global_variables" {
  path = "global_variables_generated.tf"
  if_exists = "overwrite"
  contents = <<-EOF
    variable "state_bucket_root" { type = string }
    variable "this_project" { type = string }
    variable "repo_root" { type = string }
  EOF
}

terraform {
  before_hook "init" {
    commands = ["plan", "apply", "import", "refresh"]
    execute = ["terraform", "get", "-update"]
  }

  extra_arguments "no_plan_lock" {
    commands = ["plan"]

    arguments = ["-lock=false"]
  }

  after_hook "rm_backend_tf" {
    commands = ["apply","console","destroy","env","fmt","get","graph","import","output","plan","refresh","show","taint","untaint","validate","workspace"]
    execute = [
      "rm",
      "-f",
      "${get_terragrunt_dir()}/backend.tf"]
    run_on_error = true
  }
}
