# ADR 006: SSL Certificate Verification

## Status

Proposed

## Context

Users are experiencing SSL certificate verification failures when connecting to Sumo Logic API:

```
Error: Search failed: SSL_connect returned=1 errno=0 peeraddr=52.25.140.7:443
state=error: certificate verify failed (unable to get certificate CRL)
```

### Root Cause

The issue occurs when:
1. Ruby's OpenSSL points to a certificate path that doesn't exist
2. System CA certificates are not properly configured
3. The certificate store cannot verify the Sumo Logic API certificate chain

### Current Implementation

The `ConnectionPool` class creates SSL connections but doesn't explicitly configure certificate verification:

```ruby
def create_connection(uri)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  # No explicit SSL certificate configuration
  http.start
  http
end
```

## Problem

SSL certificate verification is critical for security, but the current implementation doesn't handle common certificate store issues on different systems (macOS, Linux, different OpenSSL installations).

## Options Considered

### Option 1: Use System Default Certificate Store (Current)

```ruby
def create_connection(uri)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_PEER
  http.cert_store = ssl_cert_store
  http.start
  http
end

def ssl_cert_store
  store = OpenSSL::X509::Store.new
  store.set_default_paths
  store
end
```

**Pros:**
- Simple and standard approach
- Uses OS-provided certificates
- No external dependencies

**Cons:**
- Fails when system certificates are missing or misconfigured
- Requires users to fix their OpenSSL installation
- Different behavior across systems

### Option 2: Add `certifi` Gem Dependency

```ruby
# Gemfile
gem 'certifi'

# connection_pool.rb
require 'certifi'

def ssl_cert_store
  store = OpenSSL::X509::Store.new
  store.add_file(Certifi.where)
  store
end
```

**Pros:**
- Bundles Mozilla's CA certificates
- Works consistently across all platforms
- Handles certificate updates via gem updates

**Cons:**
- Adds external dependency
- Increases gem size
- Requires maintaining another dependency

### Option 3: Fallback Chain with Multiple Certificate Sources

```ruby
def ssl_cert_store
  store = OpenSSL::X509::Store.new
  store.set_default_paths

  # Try common certificate locations as fallbacks
  cert_paths = [
    '/etc/ssl/cert.pem',
    '/usr/local/etc/openssl/cert.pem',
    '/opt/homebrew/etc/openssl@3/cert.pem',
    ENV['SSL_CERT_FILE']
  ].compact

  cert_paths.each do |path|
    store.add_file(path) if File.exist?(path)
  rescue OpenSSL::X509::StoreError
    # Already added or invalid
  end

  store
end
```

**Pros:**
- Handles multiple environments
- No external dependencies
- Provides fallbacks

**Cons:**
- Complex logic
- Hard to maintain
- Obscures real configuration issues

### Option 4: Allow SSL Verification Disable (Development Only)

```ruby
# Configuration
class Configuration
  attr_accessor :verify_ssl  # default: true
end

# ConnectionPool
def create_connection(uri)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  if @config.verify_ssl
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER
    http.cert_store = ssl_cert_store
  else
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    warn "WARNING: SSL verification disabled!"
  end

  http.start
  http
end
```

**Pros:**
- Quick workaround for development
- User has control

**Cons:**
- Security risk if misused
- Bad practice to encourage
- Could be accidentally deployed to production

## Decision

**[TO BE DECIDED]**

## Consequences

**[TO BE DOCUMENTED AFTER DECISION]**

## Next Steps

1. Investigate the specific SSL error on the user's system
2. Determine if it's a system configuration issue or code issue
3. Test proposed solutions on multiple platforms
4. Make decision based on:
   - Security best practices
   - Ease of use
   - Maintenance burden
   - Platform compatibility

## References

- Ruby Net::HTTP SSL documentation
- OpenSSL certificate verification
- [Python's certifi approach](https://github.com/certifi/python-certifi)
- [Go's approach with embedded certs](https://pkg.go.dev/crypto/x509)
