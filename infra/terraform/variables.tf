variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "function_name" {
  type    = string
  default = "holonet-api"
}

variable "source_archive_path" {
  type        = string
  description = "Path to zip file with function source"
}

variable "backend_url_override" {
  type        = string
  default     = ""
  description = "Optional override for API Gateway backend URL (e.g., Cloud Run service URL)."
}
