---
name: omp-add-provider
description: Add, configure, or extend model providers for Oh My Pi (omp / ohmypi). Covers user-level configuration in ~/.omp/agent/models.yml (custom OpenAI-compatible endpoints, local engines like Ollama/llama.cpp/LM Studio, LiteLLM, proxy discovery, auth pinning) and codebase-level integration (CATALOG_PROVIDERS in packages/catalog and ProviderDefinition in packages/ai). Use this skill whenever the user asks to add, configure, connect, or troubleshoot an AI provider or model in omp/ohmypi.
---

# OMP (Oh My Pi) Provider Configuration Skill

Guide and workflow for adding and configuring model providers in **Oh My Pi (`omp`)**.

---

## 1. Provider Architecture in OMP

OMP separates providers and models:
- **Provider**: Account, service, or backend namespace (e.g., `anthropic`, `openai`, `ollama`, or custom `my-gateway`).
- **Model**: Concrete model under a provider, referenced as `provider/model-id` (e.g., `openai/gpt-5.4`, `my-gateway/claude-sonnet`).

A model is **available** to OMP only when:
1. Provider ID is **not** in `disabledProviders` (in `~/.omp/agent/config.yml` or `<project>/.omp/config.yml`).
2. Provider is either **keyless** (`auth: none` / local engines) **or** has resolvable credentials.

---

## 2. Choosing the Right Integration Mode

- **Mode A: User Configuration (`models.yml`)** *(Most common)*: Add custom API gateways, private endpoints, or local engines without editing OMP source code.
- **Mode B: Codebase Integration (Contributor)**: Add a first-party built-in provider to the `can1357/oh-my-pi` repository.
- **Mode C: Extension Runtime Registration**: Register dynamic providers via OMP extensions (`pi.registerProvider`).

---

## 3. Mode A: User Configuration (`models.yml`)

### File Location
- Global path: `~/.omp/agent/models.yml` (Windows: `%USERPROFILE%\.omp\agent\models.yml`)
- **Important**: Always use the `.yml` extension. Some versions may fail to recognize `.yaml`.

### Root Structure
The root object only accepts `providers:`. Unknown root keys will fail schema validation.

```yaml
providers:
  <provider-id>:
    baseUrl: <endpoint-url>
    api: <api-transport>
    apiKey: <key-or-env-name>
    # ... additional options
```

### Provider-Level Fields

| Field | Type | Description |
|---|---|---|
| `baseUrl` | `string` | Base URL of the endpoint (e.g. `https://api.example.com/v1`). |
| `api` | `string` | Wire protocol family (see allowed values below). |
| `apiKey` | `string` | API Key value, environment variable name, or `!command` stdout resolver. |
| `auth` | `apiKey` \| `none` \| `oauth` | Auth mode. Use `none` for keyless local models. Default is `apiKey`. |
| `authHeader` | `boolean` | Set `true` to inject `Authorization: Bearer <resolved-key>` on requests. |
| `disableStrictTools` | `boolean` | Set `true` for Anthropic/proxy endpoints that reject strict schema flags. |
| `headers` | `map` | Custom request headers sent to the provider. |
| `discovery` | `object` | Auto-discovery configuration (`type`, `injectV1`, `timeoutMs`). |
| `models` | `list` | Explicit list of models under this provider. |
| `modelOverrides` | `map` | Per-model property overrides by model ID. |

### Allowed `api` Transport Values
- `openai-completions`: Standard OpenAI Chat Completions (`/v1/chat/completions`).
- `openai-responses`: OpenAI Responses API (`/v1/responses`).
- `anthropic-messages`: Anthropic Messages API (`/v1/messages`).
- `google-generative-ai`: Google Gemini API.
- `azure-openai-responses`: Azure OpenAI Responses endpoint.
- `bedrock-converse-stream`: AWS Bedrock Converse stream.
- `typesafe` / `openrouter-decisions`: System One judgment APIs (used with `judge` role).

---

## 4. Configuration Recipes

### Recipe 1: Standard OpenAI-Compatible Provider
For private gateways, vLLM, DeepSeek API, or third-party proxies:

```yaml
providers:
  my-openai:
    baseUrl: https://api.my-gateway.com/v1
    api: openai-completions
    apiKey: MY_GATEWAY_API_KEY # Reads from env var if set, else literal string
    authHeader: true
    models:
      - id: custom-model
        name: Custom Fast Model
        contextWindow: 128000
        maxTokens: 8192
```

### Recipe 2: Keyless Local Engine (Ollama / llama.cpp / LM Studio)
OMP auto-discovers default local ports, but custom ports/endpoints can be configured explicitly:

```yaml
providers:
  local-ollama:
    baseUrl: http://127.0.0.1:11434
    api: openai-responses
    auth: none
    discovery:
      type: ollama
```

For custom local OpenAI-compatible endpoints with static models:

```yaml
providers:
  local-vllm:
    baseUrl: http://127.0.0.1:8000/v1
    api: openai-completions
    auth: none
    models:
      - id: qwen2.5-coder-32b
        name: Qwen 2.5 Coder 32B Local
        contextWindow: 32768
        maxTokens: 4096
```

### Recipe 3: Multi-Wire Proxy Auto-Discovery (One-API / New-API)
For aggregators serving both `/v1/messages` and `/v1/chat/completions`:

```yaml
providers:
  aggregator-proxy:
    baseUrl: https://proxy.example.com/v1
    apiKey: PROXY_API_KEY
    authHeader: true
    disableStrictTools: true # Most proxies fail on Anthropic strict tools
    discovery:
      type: proxy
```
*Note: `discovery.type: proxy` automatically detects whether each discovered model speaks `anthropic-messages` or `openai-completions` via `supported_endpoint_types`.*

### Recipe 4: LiteLLM Gateway
```yaml
providers:
  company-litellm:
    baseUrl: https://litellm.company.com/v1
    apiKey: LITELLM_KEY
    api: openai-completions
    discovery:
      type: litellm
```

### Recipe 5: CLI / Secret Manager Key Resolution (`!command`)
OMP executes shell commands prefixed with `!` to retrieve keys asynchronously (10s timeout, cached):

```yaml
providers:
  vault-provider:
    baseUrl: https://api.openai.com/v1
    api: openai-completions
    apiKey: "!op read op://developer/openai/api-key"
```

### Recipe 6: Claude Code Router (CCR) & Anthropic-Native Gateways
For CCR instances (e.g. `https://ccr.example.com/v1`) routing Anthropic requests to Codex API, Fireworks, ZAI, etc.:

```yaml
providers:
  ccr-gateway:
    baseUrl: https://ccr.example.com/v1
    api: anthropic-messages       # CCR natively translates Anthropic SSE tool events
    apiKey: sk-ccr-your-key-here
    authHeader: true
    discovery:
      type: openai-models-list     # Queries /v1/models for auto-discovery
    compat:
      replayUnsignedThinking: false # Essential for upstream OpenAI Responses API (e.g. Codex API)
    modelOverrides:
      Codex API/gpt-6-sol:
        contextWindow: 262144
        maxTokens: 131072
        reasoning: true
```

---

## 5. Mode B: Codebase Contributor Integration (Source Code)

When contributing a new built-in provider to `can1357/oh-my-pi`:

### Step 1: Catalog Half (`packages/catalog`)
Add provider descriptor to `CATALOG_PROVIDERS` in `packages/catalog/src/provider-models/descriptors.ts`:

```typescript
// packages/catalog/src/provider-models/descriptors.ts
export const CATALOG_PROVIDERS = [
  // ...
  {
    id: "my-provider",
    defaultModel: "my-model-id",
    envVars: ["MY_PROVIDER_API_KEY"],
    createModelManagerOptions: (ctx) =>
      createSimpleOpenAICompletionsOptions("my-provider", "https://api.my-provider.com/v1", ctx),
  },
] as const;
```

### Step 2: Auth Half (`packages/ai`)
Create `packages/ai/src/registry/<id>.ts`:

```typescript
// packages/ai/src/registry/my-provider.ts
import type { ProviderDefinition } from "./types.js";

export const myProviderProvider = {
  id: "my-provider",
  name: "My Provider Name",
  // Optional login hook for /login interactive menu:
  // login: async (cb) => ...
} as const satisfies ProviderDefinition;
```

### Step 3: Register in Registry List
Add import and entry into the `ALL` array in `packages/ai/src/registry/registry.ts`:

```typescript
import { myProviderProvider } from "./my-provider.js";

export const ALL = [
  // ...
  myProviderProvider,
] as const;
```

---

## 6. Mode C: Extension Runtime Registration

OMP extensions can dynamically register providers at runtime:

```typescript
pi.registerProvider({
  id: "extension-provider",
  baseUrl: "https://api.example.com/v1",
  api: "openai-completions",
  models: [
    {
      id: "ext-model-1",
      name: "Extension Model 1",
      contextWindow: 64000,
      maxTokens: 4096,
    },
  ],
});
```

---

## 7. Verification & Troubleshooting Checklist

### Verification Commands
- List available models: `omp models`
- Filter by provider or model substring: `omp models find <query>`
- Force catalog & discovery refresh: `omp models refresh`
- Test login flow: `/login <provider>`
- Check active config: `omp config get disabledProviders`

### Common Pitfalls
1. **File name must be `models.yml`**: Do not use `models.yaml`.
2. **Missing `auth: none` for local models**: Keyless endpoints will be marked unavailable unless `auth: none` is explicitly declared.
3. **Provider disabled**: Check if provider is listed in `disabledProviders` in `~/.omp/agent/config.yml` or `<project>/.omp/config.yml`.
4. **Strict tools rejection**: Third-party Anthropic-compatible proxies often return 400 for strict tools. Add `disableStrictTools: true`.
5. **Credential precedence**:
   - `CLI --api-key` > `models.yml apiKey` > `Stored OAuth` > `/login` > Process Env Var > `<cwd>/.env` > `~/.omp/agent/.env` > `~/.omp/.env` > `~/.env`.

---

### Real-World Case Studies & Troubleshooting

#### Case 1: Empty Stop / Output Token Drop on Streaming Tool Calls
- **Symptom**:
  `Error: Retry failed after 3 attempts: Assistant returned an empty stop after retry cap, but the provider billed X output tokens for it; content was generated and then dropped before delivery...`
- **Root Cause**:
  Configuring a Claude Code Router (CCR) or Anthropic-native gateway with `api: openai-completions`. When the model issues tool calls in streaming mode, the gateway's OpenAI-compatible SSE translator drops `delta.tool_calls`, yielding `delta: {}` and empty content blocks despite billing tokens.
- **Fix**:
  Change `api` to `anthropic-messages`. CCR natively translates Anthropic SSE tool use events (`content_block_start`, `input_json_delta`) without loss:
  ```yaml
  api: anthropic-messages
  discovery:
    type: openai-models-list
  ```

#### Case 2: Upstream HTTP 400 `Invalid 'input[1].content': array too long`
- **Symptom**:
  `Error: 400 {"error":{"message":"All target providers failed.","target_providers":["openai"],"target_provider_names":["codex-api::openai_responses"],"attempts":[{"message":"Invalid 'input[1].content': array too long. Expected an array with maximum length 0, but got an array with length 1 instead."}]}}`
- **Root Cause**:
  Occurs during multi-turn chats or after tool execution when previous assistant turns contained both reasoning (`thinking`) and tool calls. OMP replayed unsigned thinking blocks (`{ type: "thinking" }`), which the gateway translated into an element inside `content`. Upstream OpenAI Responses API (`codex-api::openai_responses`) strictly enforces that assistant turns with tool calls must have `content: []` (maximum length 0).
- **Fix**:
  Add `replayUnsignedThinking: false` under `compat:` in `models.yml`:
  ```yaml
  compat:
    replayUnsignedThinking: false
  ```

#### Case 3: Automated / Non-Interactive CLI Hanging on `readPipedInput`
- **Symptom**:
  `Still starting after X s — phase: readPipedInput`
- **Root Cause**:
  `omp -p` checks `process.stdin`. In automated scripts, subshells, or background processes where `stdin` remains open without EOF, OMP waits indefinitely to read piped input.
- **Fix**:
  Explicitly close `stdin` via empty pipe:
  - PowerShell: `$null | omp -p ...`
  - Bash: `omp -p ... < /dev/null`

