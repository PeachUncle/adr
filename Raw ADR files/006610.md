# ADR 0003 — Use GitHub OIDC Roles for CI/CD Instead of Long-Lived AWS Keys

## 📖 Context

Our project uses **GitHub Actions** for CI/CD:

- Build and push app images to **Amazon ECR**.
- Run Terraform `plan/apply` against AWS infrastructure.

Traditionally, this would require creating **long-lived IAM user access keys** and storing them as GitHub secrets.
However, AWS supports **OpenID Connect (OIDC)** integration with GitHub, allowing workflows to assume IAM roles **without static keys**.

## ✅ Decision

We will configure **GitHub OIDC → AWS IAM roles** for CI/CD pipelines.

- Terraform workflow role: assume role with `AdministratorAccess` (scoped to project account) for `plan/apply`.
- App CI workflow role: assume role with ECR push permissions only.

Workflows will request short-lived credentials at runtime via OIDC federation.

## 🎯 Consequences

**Pros:**

- **No static secrets** in GitHub → eliminates key leakage risk.
- **Least privilege:** separate roles for infra and app workflows.
- **Automatic rotation:** credentials expire after job completes.
- **Auditability:** CloudTrail logs every assume-role event with GitHub repo context.

**Cons:**

- More setup complexity (OIDC provider + trust policies).
- Requires initial bootstrapping with admin access to configure roles.
- Limited regional availability when OIDC was first released (now stable).

## 🔄 Alternatives Considered

1. **Static IAM user keys stored in GitHub Secrets**

   - + Simple to configure.
   - – Risk of key compromise (secrets leak).
   - – Manual rotation burden.
2. **Self-hosted runners with IAM roles attached**

   - + Tight AWS integration.
   - – Requires operating GitHub runners inside AWS.
   - – More moving parts; not portable.
3. **HashiCorp Vault or Secrets Manager broker**

   - + Secure key storage and rotation.
   - – Adds infrastructure overhead and complexity.

## 📌 Status

Accepted — GitHub OIDC roles are the modern best practice for AWS CI/CD.We will provision two roles in `infra/modules/iam`:

- `ci-terraform-role` → Assume for Terraform plans/applies.
- `ci-ecr-push-role` → Assume for app build & push jobs.
