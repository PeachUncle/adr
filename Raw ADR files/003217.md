# ADR 027: Self-Contained Agent Functions with Environment Detection

## Status

Accepted – 2025-10-11

Supersedes: **ADR-026** (Local Agent Runner First, Netlify Function Second)

## Context

The original architecture (ADR-026) proposed separate "runner" modules (`quoteAgentRunner.js`, `triageAgentRunner.js`) that would be wrapped by Netlify functions. This approach created:
- Code duplication between runners and function wrappers
- Import complexity and potential circular dependencies
- Maintenance burden keeping two files synchronized
- Confusing architecture with multiple entry points

The agents are YAML-driven workflows that need to work in two environments:
1. **Local development**: Express server with `./startup.sh`
2. **Production**: Netlify serverless functions

## Decision

**Consolidate all agent logic into self-contained Netlify function files with environment detection.**

### Architecture Pattern

1. **Single Source of Truth Per Agent**
   - `packages/backend/netlify/functions/quote-agent.mjs` (~500 LOC, self-contained)
   - `packages/backend/netlify/functions/triage-agent.mjs` (~350 LOC, self-contained)
   - All helper functions, YAML loading, OpenAI integration, and business logic inline

2. **Environment Detection**
   ```javascript
   const isNetlify = process.env.NETLIFY === 'true' || process.env.AWS_LAMBDA_FUNCTION_NAME;

   // Conditional YAML path resolution
   let YAML_PATH;
   if (isNetlify) {
     YAML_PATH = path.resolve(process.cwd(), 'agents/quote-agent.yaml');
   } else {
     YAML_PATH = path.resolve(__dirname, '../../../../agents/quote-agent.yaml');
   }
   ```

3. **Local Development via Proxy Routes**
   - Express routes dynamically import Netlify function handlers
   - `/api/agents/quote/run` → calls `quote-agent.mjs` handler
   - Controllers import handlers when needed (e.g., `triageController.js`)
   - No separate runner files needed

4. **Production Direct Access**
   - Frontend calls `/.netlify/functions/quote-agent` in production
   - Same code, different invocation path

### Example: Quote Agent Proxy (Local Dev)

```javascript
// packages/backend/api/routes/agentRoutes.js
router.post('/quote/run', async (req, res) => {
  try {
    // Dynamically import the Netlify function handler
    const { handler } = await import('../../netlify/functions/quote-agent.mjs');

    // Transform Express request to Netlify event format
    const event = {
      httpMethod: 'POST',
      body: JSON.stringify(req.body),
      headers: req.headers
    };

    // Call the handler
    const result = await handler(event, {});

    // Send response
    res.status(result.statusCode).json(JSON.parse(result.body));
  } catch (error) {
    res.status(500).json({ error: 'Agent execution failed' });
  }
});
```

## Consequences

### Benefits
- ✅ **Single source of truth** - All logic in one file per agent
- ✅ **Simpler architecture** - No abstraction layers
- ✅ **Environment-agnostic** - Same code works locally and on Netlify
- ✅ **Easier debugging** - All code in one place
- ✅ **Faster cold starts** - Fewer module loads (important for serverless)
- ✅ **Less maintenance** - ~700 LOC removed, 2 files eliminated
- ✅ **Clear ownership** - Each function is independently deployable

### Trade-offs
- ⚠️ Larger function files (~500 LOC vs ~100 LOC wrapper + ~400 LOC runner)
  - **Mitigation**: Still manageable size, well-organized with helper functions
- ⚠️ Local development uses Express proxy routes
  - **Mitigation**: Minimal boilerplate, same pattern as quote/triage agents

### Maintained Principles
- ✅ YAML remains single source of truth for workflow definitions
- ✅ Environment variables control sensitive data (OpenAI API keys)
- ✅ Netlify `functions` configuration in `netlify.toml` handles dependencies

## Migration Summary

### Deleted Files
- ❌ `packages/backend/api/agents/quoteAgentRunner.js` (~450 LOC)
- ❌ `packages/backend/api/agents/triageAgentRunner.js` (~250 LOC)

### Enhanced Files
- ✅ `packages/backend/netlify/functions/quote-agent.mjs` - Now self-contained (~500 LOC)
- ✅ `packages/backend/netlify/functions/triage-agent.mjs` - Now self-contained (~350 LOC)

### Updated Files
- ✅ `packages/backend/api/routes/agentRoutes.js` - Simple proxy
- ✅ `packages/backend/api/controllers/triageController.js` - Calls function handler
- ✅ `packages/backend/api/routes/requestRoutes.js` - Removed runner import
- ✅ `packages/frontend/src/features/requests/components/QuoteAgentModal.tsx` - Environment-based endpoint

### Net Impact
- **Code reduction**: ~700 LOC total removed
- **File reduction**: 2 files eliminated
- **Complexity reduction**: Single entry point per agent

## Implementation Details

### Quote Agent Function Structure
```javascript
// packages/backend/netlify/functions/quote-agent.mjs

import fs from 'fs';
import path from 'path';
import YAML from 'yaml';
import OpenAI from 'openai';

// Environment detection
const isNetlify = process.env.NETLIFY === 'true' || process.env.AWS_LAMBDA_FUNCTION_NAME;

// YAML loading (environment-aware paths)
const yamlConfig = YAML.parse(fs.readFileSync(YAML_PATH, 'utf-8'));

// Session storage
const sessions = new Map();

// Helper functions
function getNodeById(nodeId) { /* ... */ }
function normalizeServiceKey(value) { /* ... */ }
function createSession(sessionId) { /* ... */ }

// Core agent logic
async function runQuoteAgent({ sessionId, messages }) { /* ... */ }

// Netlify function handler
export async function handler(event, context) {
  // CORS, validation, error handling
  const result = await runQuoteAgent({ sessionId, messages });
  return { statusCode: 200, body: JSON.stringify(result) };
}
```

## Testing Strategy

1. **Local Development**: Test via Express routes (`/api/agents/quote/run`)
2. **Netlify Dev**: Test with `netlify dev` (simulates production)
3. **Production**: Deployed functions at `/.netlify/functions/*`

## Related ADRs

- **ADR-014**: Pure ESM Strategy (enables dynamic imports)
- **ADR-015**: Monorepo Structure (workspace organization)
- **ADR-025**: OpenAI Agent Toolkit Implementation Pattern (YAML-driven workflows)
- **ADR-026**: Local Agent Runner First (superseded by this ADR)

## Future Considerations

- **Consider Netlify Dev as primary local development tool** instead of Express proxy routes
- **Monitor function file sizes** - if functions exceed ~1000 LOC, consider splitting helpers into shared modules
- **Evaluate caching strategies** for YAML loading in production (currently loads on cold start)
