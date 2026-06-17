# Terraform Cost Policy Guard Case Study

## Problem

Infrastructure teams often catch cost spikes and unsafe security-group changes too late, after a Terraform plan is already moving through a release pipeline. I wanted a compact project that proves I can turn that review step into a repeatable platform control instead of a manual checklist.

## Goal

Build a recruiter-readable service that can:

- evaluate Terraform plan JSON with deterministic rules
- fail a pipeline when a plan is risky
- expose an API for shared tooling
- ship with the packaging and deployment assets expected in a production-shaped repo

## Design Choices

- FastAPI keeps the service simple while still showing API design, health checks, and metrics endpoints.
- The same `evaluate_plan` function powers both the HTTP service and the CLI so the behavior stays consistent across local use and CI/CD.
- Policy checks focus on practical platform risks:
  - destructive changes on stateful resources
  - open ingress on sensitive ports
  - missing ownership and environment tags
  - monthly cost delta above a release threshold

## Verification Strategy

- unit tests verify safe and risky fixtures
- API tests prove the service contract
- CLI execution proves pipeline ergonomics
- a real container build proves packaging works

## Why This Helps My Portfolio

This repo is stronger than a toy Terraform script because it shows the surrounding engineering work: change safety logic, testability, deploy artifacts, operational endpoints, and documentation that a platform or SRE hiring manager can scan quickly.
