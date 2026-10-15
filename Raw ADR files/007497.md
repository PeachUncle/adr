# ADR-007 – SSL Certificate: Manual Let's Encrypt on Free Tier

**Status:** Accepted  
**Date:** 2025-11-12  
**Author:** Niklas Häll

---

## Context
The project requires HTTPS for the custom domain `ticket.mymh.dev` to ensure secure communication and meet modern web standards.  
Azure App Service on Free tier (F1) does not support App Service Managed Certificates, which are only available on Basic tier and above.  
The project has a limited duration (6 weeks remaining), so long-term certificate management and auto-renewal are not critical requirements.  
Cost optimization is a priority, so staying on Free tier is preferred.

---

## Decision
We use **manual Let's Encrypt certificates** with **DNS-01 challenge validation** for SSL/TLS on the custom domain.  
The certificate is generated using **certbot via Docker** (since Docker is available on the development machine), converted to PFX format using OpenSSL in Docker, and manually uploaded to Azure App Service.  
This approach allows us to:
- Stay on Free tier App Service (F1)
- Use a trusted, free SSL certificate (Let's Encrypt)
- Control the validation process via DNS records we manage at Loopia
- Avoid additional Azure costs
- Use Docker (already available) without requiring local tool installation

The DNS-01 challenge method is chosen because we have full control over DNS records, making validation straightforward and reliable.

**Note:** Azure Key Vault will be used later in the project for storing secrets and connection strings. While Key Vault can also store certificates, for this initial setup we upload directly to App Service to keep the process simple and cost-effective. Future certificate management could leverage Key Vault if needed.

---

## Consequences
**Advantages:**  
- No additional Azure costs (stays on Free tier).  
- Uses trusted Let's Encrypt certificates (recognized by all browsers).  
- DNS-01 challenge is reliable and doesn't require local port access.  
- Certificate is valid for 90 days, which covers the remaining project duration.  

**Disadvantages:**  
- Manual process requires certbot and OpenSSL tools.  
- No automatic renewal (not needed for 6-week project).  
- Certificate must be manually uploaded and bound in Azure.  
- Requires DNS access for validation.  

---

## Risks / Mitigations
- **Risk:** Certificate generation process may be complex for team members unfamiliar with certbot.  
  **Mitigation:** Document the process clearly in this ADR with step-by-step instructions.  

- **Risk:** Certificate could expire if project extends beyond 90 days.  
  **Mitigation:** Project duration is 6 weeks, well within the 90-day validity period.  

- **Risk:** Manual upload process could introduce errors.  
  **Mitigation:** Use Azure CLI commands with clear verification steps.  

---

## Alternatives
- **App Service Managed Certificate:** Free and automatic, but requires Basic tier (B1) at ~$10-13/month. Rejected due to cost optimization priority.  
- **Azure Key Vault certificate storage:** Key Vault will be used later in the project for secrets management. While it can store certificates, uploading directly to App Service is simpler for initial setup and avoids additional Key Vault operations costs during MVP phase. Certificate storage in Key Vault could be considered for future iterations.  
- **Local certbot installation:** Requires installing certbot and OpenSSL locally. Rejected in favor of Docker approach since Docker is already available and avoids local tool management.  
- **Commercial SSL certificate:** Costs money and unnecessary when free options exist.  
- **HTTP only (no SSL):** Not acceptable for modern web applications and security standards.  

---

## Technical Implementation Guide

### Prerequisites
- Custom domain configured in Azure App Service
- DNS CNAME pointing to App Service default hostname
- Docker installed and running
- Azure CLI configured

### Step 1: Generate Let's Encrypt Certificate (DNS-01 Challenge)

Using Docker for certbot (recommended approach):

```bash
# Generate certificate using Docker
docker run -it --rm \
  -v "${PWD}/letsencrypt:/etc/letsencrypt" \
  certbot/certbot certonly --manual --preferred-challenges dns -d your-domain.com
```

**On Windows PowerShell:**
```powershell
docker run -it --rm `
  -v "${PWD}/letsencrypt:/etc/letsencrypt" `
  certbot/certbot certonly --manual --preferred-challenges dns -d your-domain.com
```

Certbot will prompt you to add a TXT record to your DNS. Add it at your DNS provider (e.g., Loopia), wait a few minutes for propagation, then press Enter in certbot to continue.

Certificates will be created in the local `letsencrypt/live/your-domain.com/` directory (mounted from Docker volume).

Files created:
- `fullchain.pem` (certificate chain)
- `privkey.pem` (private key)

### Step 2: Convert to PFX Format (Azure requires PFX)

Using Docker for OpenSSL conversion:

```bash
# Convert to PFX using Docker
docker run -it --rm \
  -v "${PWD}/letsencrypt:/etc/letsencrypt" \
  -v "${PWD}:/output" \
  alpine/openssl pkcs12 -export \
    -out /output/your-domain.com.pfx \
    -inkey /etc/letsencrypt/live/your-domain.com/privkey.pem \
    -in /etc/letsencrypt/live/your-domain.com/fullchain.pem \
    -name "your-domain.com" \
    -passout pass:YOUR_PASSWORD
```

**On Windows PowerShell:**
```powershell
docker run -it --rm `
  -v "${PWD}/letsencrypt:/etc/letsencrypt" `
  -v "${PWD}:/output" `
  alpine/openssl pkcs12 -export `
    -out /output/your-domain.com.pfx `
    -inkey /etc/letsencrypt/live/your-domain.com/privkey.pem `
    -in /etc/letsencrypt/live/your-domain.com/fullchain.pem `
    -name "your-domain.com" `
    -passout pass:YOUR_PASSWORD
```

Replace `YOUR_PASSWORD` with a secure password - this will be needed when uploading to Azure.

### Step 3: Upload Certificate to Azure App Service

```bash
# Upload the certificate
az webapp config ssl upload \
  --name YOUR_APP_SERVICE_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --certificate-file your-domain.com.pfx \
  --certificate-password "YOUR_PFX_PASSWORD"
```

### Step 4: Bind Certificate to Custom Domain

```bash
# Get the certificate thumbprint
az webapp config ssl list \
  --name YOUR_APP_SERVICE_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --query "[?name=='your-domain.com'].thumbprint" -o tsv

# Bind the certificate (replace THUMBPRINT with actual value)
az webapp config ssl bind \
  --name YOUR_APP_SERVICE_NAME \
  --resource-group YOUR_RESOURCE_GROUP \
  --certificate-thumbprint THUMBPRINT \
  --ssl-type SNI \
  --hostname your-domain.com
```

### Alternative: Local Certbot Installation

If Docker is not available, certbot can be installed locally:

```bash
# macOS
brew install certbot

# Linux
sudo apt-get install certbot

# Generate certificate
certbot certonly --manual --preferred-challenges dns -d your-domain.com

# Convert to PFX (requires OpenSSL)
openssl pkcs12 -export \
  -out your-domain.com.pfx \
  -inkey /etc/letsencrypt/live/your-domain.com/privkey.pem \
  -in /etc/letsencrypt/live/your-domain.com/fullchain.pem \
  -name "your-domain.com"
```

**Note:** Docker approach is preferred since it's already available and avoids local tool installation.

### Verification

After binding, verify SSL is working:
```bash
curl -I https://your-domain.com
```

Or visit the domain in your browser and verify the SSL certificate is valid.

### Notes

- Let's Encrypt certificates are valid for 90 days
- Certificate persists in Azure across deployments
- No renewal needed for this project's duration
- Keep the PFX file and password secure (do not commit to repository)
- **Future consideration:** Azure Key Vault (already planned for the project) could be used to store the certificate and PFX password for improved security and centralized secret management

---

## References
- [System overview](../initial_outtakes/system_overview.md)  
- [Microsoft Docs – App Service SSL certificates](https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate)  
- [Let's Encrypt documentation](https://letsencrypt.org/docs/)  
- [Certbot documentation](https://eff-certbot.readthedocs.io/)

