output "gateway_url" {
  value = google_api_gateway_gateway.holonet.default_hostname
}

output "function_url" {
  value = google_cloudfunctions2_function.holonet.service_config[0].uri
}

output "backend_url" {
  value = local.backend_url
}
