terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  backend_url = var.backend_url_override != "" ? var.backend_url_override : google_cloudfunctions2_function.holonet.service_config[0].uri
}

resource "google_storage_bucket" "source" {
  name          = "${var.project_id}-holonet-source"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "holonet-src.zip"
  bucket = google_storage_bucket.source.name
  source = var.source_archive_path
}

resource "google_cloudfunctions2_function" "holonet" {
  name     = var.function_name
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "app"
    source {
      storage_source {
        bucket = google_storage_bucket.source.name
        object = google_storage_bucket_object.archive.name
      }
    }
  }

  service_config {
    available_memory   = "512M"
    timeout_seconds    = 30
    max_instance_count = 5
    environment_variables = {
      SWAPI_BASE_URL           = "https://swapi.dev/api"
      CACHE_TTL_SECONDS        = "180"
      CACHE_BACKEND            = "inmemory"
      HTTP_TIMEOUT_SECONDS     = "6"
      HTTP_RETRIES             = "2"
      MAX_PAGE_SIZE            = "50"
      MAX_UPSTREAM_PAGES       = "6"
      MAX_EXPAND_CONCURRENCY   = "8"
      REQUIRE_API_KEY          = "false"
      API_PAGE_SIZE_DEFAULT    = "10"
    }
  }
}

resource "google_api_gateway_api" "holonet" {
  api_id = "holonet-api"
}

resource "google_api_gateway_api_config" "holonet" {
  api           = google_api_gateway_api.holonet.api_id
  api_config_id = "holonet-config"

  openapi_documents {
    document {
      path     = "api/openapi-gateway.yaml"
      contents = templatefile("${path.module}/openapi-template.yaml", {
        backend_url = local.backend_url
      })
    }
  }
}

resource "google_api_gateway_gateway" "holonet" {
  gateway_id = "holonet-gw"
  api_config = google_api_gateway_api_config.holonet.id
  region     = var.region
}
