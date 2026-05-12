## Why

The backend route modules currently mix HTTP routing concerns with business logic, which makes the code harder to maintain, test, and extend. Splitting controller logic out of route files now will reduce duplication, make endpoint behavior easier to reason about, and let future API changes stay localized.

## What Changes

- Move business logic out of `app/routes/*` into dedicated controller modules.
- Keep route files focused on HTTP concerns such as path, method, request parsing, and response delivery.
- Preserve existing endpoint URLs, status codes, and response contracts while changing the internal structure.
- **BREAKING**: Internal module structure will change, so direct imports from route files for business logic will no longer be valid.
- Add or update tests to cover controller behavior and route delegation.

## Capabilities

### New Capabilities
- `route-controller-split`: Backend routes delegate business logic to controllers while routes remain thin HTTP adapters.

### Modified Capabilities
- 

## Impact

Affected backend route modules, new controller modules, shared service calls, and backend tests. Backend developers will work with a clearer separation of concerns, while frontend consumers should see no contract change if endpoint behavior is preserved.
