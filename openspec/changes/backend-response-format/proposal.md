## Why

The backend currently returns inconsistent API payloads across routes, which makes frontend integration and error handling harder than it needs to be. Standardizing every response now reduces coupling, improves predictability for consumers, and creates one response contract the UI can rely on.

## What Changes

- Standardize successful API responses to use a shared envelope with `status`, `message`, and `data`.
- Standardize error responses to use the same envelope shape so clients can handle success and failure consistently.
- Update backend route handlers, exception handling, and shared response utilities to emit the new contract.
- **BREAKING**: Response bodies will no longer return ad hoc top-level payloads from endpoints.
- Add tests to verify the response shape across representative endpoints.

## Capabilities

### New Capabilities
- `api-response-format`: Consistent API response envelope for success and error cases across backend endpoints.

### Modified Capabilities
- 

## Impact

Affected backend route handlers, global exception handling, shared response utilities, and API tests. Frontend consumers will need to read `status`, `message`, and `data` instead of depending on endpoint-specific top-level payloads.
