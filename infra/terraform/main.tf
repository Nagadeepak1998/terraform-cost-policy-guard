terraform {
  required_version = ">= 1.6.0"
}

variable "image" {
  type        = string
  description = "Container image to deploy."
}

resource "kubernetes_namespace" "this" {
  metadata {
    name = "terraform-cost-policy-guard"
  }
}

resource "kubernetes_manifest" "deployment" {
  manifest = yamldecode(templatefile("${path.module}/templates/deployment.yaml.tftpl", {
    image = var.image
  }))
}
