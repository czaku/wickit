# Wickit v0.2.0 Roadmap

## New Modules to Add

### ~~1. `orchestrator` - Task Orchestration~~ ❌ NOT MOVING

**Decision:** Keep in ralfie/ralfiepretzel (2026-01-22)

**Reasoning:**
- Orchestrator is tightly coupled to ralfie's REQ-driven workflow
- Uses omnai for AI execution (shared layer already exists)
- Git commit semantics are ralfie-specific, not generic
- Simpler to iterate without cross-repo coordination
- If other projects need it later, can reconsider

**Where it lives instead:**
- `ralfie/lib/task-runner.sh` - Task execution with fresh context
- `omnai` - AI execution and context health (shared)
- `ralfiepretzel` - REQ parsing and validation

### 2. `scheduler` - Task Scheduling
**From:** ralfiepretzel's orchestration.scheduler

**Features:**
- Cron-like scheduling
- One-time scheduled tasks
- Task prioritization
- Execution history
- Retry policies

**Use cases:**
- Background job processing
- Periodic syncs
- Scheduled backups
- Automation workflows

### 3. `skills` - Skill/Plugin Registry
**From:** ralfiepretzel's skills module

**Features:**
- Plugin discovery and registration
- Skill versioning
- Dependency management between skills
- Hot-reloading support
- Skill metadata

**Use cases:**
- Plugin systems
- Extensible applications
- Skill/agent management
- Modular architectures

### 4. `importer` - Import/Export Utilities
**From:** jobforge's import_export module

**Features:**
- JSON Resume import/export
- LinkedIn profile import
- Generic JSON import
- Format auto-detection
- Data transformation

**Use cases:**
- Resume parsing
- Profile migration
- Data interoperability
- Format conversion

### 5. `cipher` - Encryption
**From:** jobforge's encryption module

**Features:**
- AES-256-GCM encryption
- Password-based key derivation (PBKDF2)
- File encryption
- Directory archiving
- Secure password prompting

**Use cases:**
- Sensitive data protection
- Encrypted backups
- Secure storage
- Credential management

## Current Wickit v0.1.0 Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `hideaway` | Data directory management | ✅ Done |
| `knobs` | Configuration management | ✅ Done |
| `dropzone` | File operations | ✅ Done |
| `cloudbridge` | Cloud sync (Dropbox, GDrive) | ✅ Done |
| `autopilot` | CLI framework (Click) | ✅ Done |
| `synapse` | AI runner integration | ✅ Done |
| `pulse` | Progress indicators | ✅ Done |
| `blueprint` | JSON Schema validation | ✅ Done |
| `humanize` | Formatting utilities | ✅ Done |
| `landscape` | Path operations | ✅ Done |

## Proposed v0.2.0 Modules

| Module | Priority | Source | Status |
|--------|----------|--------|--------|
| ~~`orchestrator`~~ | ~~High~~ | ~~ralfiepretzel~~ | ❌ Not moving (stays in ralfie) |
| `scheduler` | High | ralfiepretzel | Planned |
| `skills` | Medium | ralfiepretzel | Planned |
| `importer` | Medium | jobforge | Planned |
| `cipher` | Medium | jobforge | Planned |
| `projects` | Low | ralfiepretzel | Planned |
| `requirements` | Low | ralfiepretzel | Planned |

## Implementation Order

### Phase 1: Core Infrastructure
1. `cipher` - Already implemented in jobforge
2. `importer` - Already implemented in jobforge

### Phase 2: Workflow
3. `scheduler` - Task scheduling (orchestrator stays in ralfie)

### Phase 3: Extensibility
5. `skills` - Plugin registry
6. `projects` - Project management

## Dependencies to Add

```toml
# pyproject.toml additions for v0.2.0

[dependencies]
# Existing
click >= 8.0
rich >= 13.0
pydantic >= 2.0
jsonschema >= 4.0

# New for orchestrator
networkx >= 2.8  # For dependency graphs

# New for scheduler
apscheduler >= 3.10  # For cron scheduling (optional, can be pure Python)

# New for cipher (already have cryptography in jobforge)
cryptography >= 41.0
```

## Migration Guide

### From v0.1.0 to v0.2.0

All existing modules remain compatible. New modules are opt-in:

```python
# Existing v0.1.0 code continues to work
from wickit import hideaway, knobs, dropzone

# New v0.2.0 modules available
from wickit import orchestrator, scheduler, skills, importer, cipher
```

## Testing Strategy

Each new module should have:
- Unit tests for core functionality
- Integration tests with dependent repos
- Type hints and mypy compliance
- Documentation with examples

## Release Checklist

- [ ] Port `cipher` from jobforge
- [ ] Port `importer` from jobforge
- [x] ~~Port `orchestrator` from ralfiepretzel~~ - Decision: NOT MOVING (stays in ralfie)
- [ ] Port `scheduler` from ralfiepretzel
- [ ] Port `skills` from ralfiepretzel
- [ ] Write tests for all new modules
- [ ] Update README with new modules
- [ ] Create migration guide
- [ ] Tag v0.2.0 release
- [ ] Update dependent repos (jobforge, studya, ralfiepretzel)

## Related Issues

- jobforge already uses `cipher` and `importer` modules directly
- ralfiepretzel uses `blueprint` for validation
- All repos can benefit from `orchestrator` and `scheduler`
