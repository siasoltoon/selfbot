# Plugin System

## Purpose
Plugins provide independently replaceable feature modules without turning the core into a monolith.

## Contract
Each plugin declares a unique identifier, version, core API compatibility, dependencies, configuration schema, capabilities, requested permissions, lifecycle hooks when needed, documentation and tests.

A manifest is metadata only. The core owns authorization and lifecycle decisions.

## Lifecycle
DISCOVER -> VALIDATE -> RESOLVE DEPENDENCIES -> AUTHORIZE -> LOAD -> ENABLE -> RUN -> DISABLE

Invalid plugins fail closed and do not partially register commands.

## Isolation
Plugins use stable core interfaces for events, commands, tasks, storage, configuration, logging and permissions. Plugins must not bypass permission checks, expose secrets through logs, assume a deployment provider, or report an external action as successful without confirmation.

## Configuration
Secrets remain in environment/configuration. User/plugin settings are schema-validated and scoped to the appropriate owner or administrator.

## Dependencies
Dependencies are explicit and circular dependencies are rejected. Optional integrations must not prevent unrelated plugins from loading.

## Commands
The core command registry owns aliases, argument validation, permissions, help metadata, execution lifecycle and error handling.

## Testing
Production plugins require manifest, lifecycle, permission and failure-path tests, plus command/service tests where applicable.

## Versioning
Plugin versions follow semantic versioning where practical. Compatibility is checked against the core plugin API before activation.
