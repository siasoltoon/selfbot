# Telegram Personal AI Operating System — Master Engineering Specification

Repository: `siasoltoon/selfbot`

This document is the authoritative long-form master specification for the project. Project Instructions are the operating rules; this document is the product/architecture roadmap. Conversation prompts must use the engineering-memory files to resume from the exact incomplete task.

## 1. PROJECT MISSION

Build a complete Telegram Personal AI Operating System combining:

- Telegram Self Bot automation
- AI personal assistant
- Long-term memory
- Continuous AI chat
- Voice assistant
- Web intelligence
- Plugin ecosystem
- PC Worker processing
- Web administration panel
- Advanced automation engine
- Security
- Backup and restore
- Analytics
- Smart storage
- Controlled self-learning
- Multi-agent AI capabilities

The final platform must be modular, scalable, maintainable, secure, deployment-agnostic and production-ready.

## 2. PROJECT PRINCIPLES

- Build on the actual repository state.
- Preserve working functionality.
- Avoid unnecessary rewrites and duplication.
- Use clean modular architecture.
- Keep major capabilities independently replaceable.
- Never hardcode secrets.
- Use environment variables and configuration.
- Centralize validation, errors and structured logging.
- Every major feature requires tests and documentation.
- Never claim success without validation.
- No fake implementations or fabricated external-service results.
- Security-sensitive operations must fail safely.
- Maintain persistent engineering memory.

## 3. DEPLOYMENT-AGNOSTIC ARCHITECTURE

The application MUST NOT depend on Railway.

The same codebase must support:

1. Railway
2. Standard VPS
3. GitHub-hosted/temporary VPS or limited-runtime server environments
4. Personal PC/Laptop

Use a shared application core with deployment-specific infrastructure/configuration/adapters.

Core business logic must not contain Railway-only assumptions.

Support where appropriate:

- Docker
- Docker Compose
- environment configuration
- health checks
- graceful startup/shutdown
- restart/recovery
- configurable database/services
- local execution
- remote execution
- optional worker execution

A deployment target being unavailable must not break unrelated lightweight functionality.

## 4. PERSISTENT ENGINEERING MEMORY

Maintain:

docs/engineering/PROJECT_STATE.md
docs/engineering/ARCHITECTURE_MAP.md
docs/engineering/PHASE_STATE.md
docs/engineering/TASK_STATE.md
docs/engineering/TEST_STATE.md
docs/engineering/DECISIONS.md
docs/engineering/CHANGELOG_ENGINEERING.md

These files are the authoritative continuation state.

Record current phase/task, completed work, remaining work, tests, failures/fixes, decisions, architecture changes, deployment status, limitations and exact next step.

A new conversation must be able to continue without repeating a full repository investigation.

## 5. TARGET ARCHITECTURE

Telegram Client
→ Event Router
→ Core Engine
→ Plugin System
→ Task Manager
→ Queue
→ Workers
→ External Services

Core domains may include:

app/core/
- events
- commands
- tasks
- scheduler
- security
- database
- logging
- config

plugins/
- ai
- voice
- web
- automation
- downloader
- games
- profile
- finance
- utilities

worker/
- ai_worker
- voice_worker
- media_worker
- processing_worker

dashboard/
- web_admin

tests/
docs/
docker/
config/

The exact structure may evolve when justified by architecture decisions.

## 6. PHASE ROADMAP

### PHASE 0 — PROJECT BOOTSTRAP

Establish repository foundation:

- README
- LICENSE
- .gitignore
- environment configuration
- source structure
- tests
- docs
- engineering memory
- development/main workflow

Do not destroy or replace useful existing repository content.

### PHASE 1 — SYSTEM ARCHITECTURE DESIGN

Define and document:

- technology stack
- application structure
- database architecture
- event system
- task system
- plugin system
- worker communication
- security model
- API design
- deployment model
- Railway/VPS/temporary-server/PC portability

Create/update:

- docs/ARCHITECTURE.md
- docs/DATABASE_DESIGN.md
- docs/PLUGIN_SYSTEM.md
- docs/WORKER_ARCHITECTURE.md
- docs/SECURITY_MODEL.md
- docs/API_DESIGN.md

### PHASE 2 — CORE FOUNDATION

Implement:

Configuration:
- environment variables
- development/production modes
- secret handling

Database:
- users
- settings
- plugins
- AI memory
- tasks
- logs
- analytics

Logging:
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL
- structured logging

Exceptions:
- unified exceptions
- classification
- recovery
- safe failure

Event bus:
- new message
- edited message
- media
- command
- timer
- worker response

Command registry:
- commands
- aliases
- permissions
- arguments
- validation
- help

Task manager:
- create
- queue
- execute
- cancel
- retry
- status

Scheduler:
- one-time
- daily
- weekly
- cron/custom schedules

### PHASE 3 — PLUGIN SYSTEM

Every plugin should have:

- manifest
- configuration
- commands
- services
- models when needed
- tests
- documentation

Support:

- enable/disable
- settings
- versioning
- dependencies
- lifecycle validation

### PHASE 4 — TELEGRAM SELF BOT CORE

Implement base Telegram functionality.

Self management:
- enable/disable
- status
- ping
- ID information
- session management

Profile:
- name
- last name
- bio
- profile picture
- configurable fonts/styles
- date/clock styles

PV/group management:
- mandatory join where applicable
- PV lock
- enemy list
- block
- silence
- word filter
- tagging
- group management

All actions require permission and safety validation.

### PHASE 5 — AUTOMATION FEATURES

Auto systems:

- auto reaction
- auto reply
- auto seen
- auto comments
- banner
- secretary mode

Content system:

- save content
- keyword triggers
- text
- photo
- video
- sticker
- GIF

Text formatting:

- bold
- italic
- mono
- configurable/random styles

### PHASE 6 — GAME AND ECONOMY SYSTEM

Implement modular game integrations where applicable:

- Mew automation
- fishing
- Pishi
- factory/production
- selling/market/product logic

Use isolated plugins so these features cannot destabilize the core.

### PHASE 7 — AI PERSONAL ASSISTANT

Architecture:

User Input
→ AI Router
→ Intent Detection
→ Memory Retrieval
→ AI Processing
→ Response Generation

Implement:

- provider/model abstraction
- continuous conversation
- context management
- action/tool boundaries
- safe action execution

Memory:

- save user facts
- preferences
- projects
- important information
- retrieve/search
- update
- forget/delete
- export
- categories
- permission controls
- validation

AI chat mode:

- private chat
- selected users/groups
- time restrictions
- cooldown
- conversation history

Summarizer:

- message
- conversation
- article
- document
- short summary
- important points
- action items

Translator:

- language detection
- translation
- automatic translation
- PV/group/selected-user scopes

### PHASE 8 — WEB INTELLIGENCE

Architecture:

Request
→ AI Router
→ Web decision
→ Search
→ Extraction
→ Analysis
→ Response

Implement:

- internet search
- result filtering
- source collection
- summaries
- URL analysis
- title/description/content extraction
- technology detection
- security/risk indicators
- article/documentation/news/blog summarization

Never fabricate web results.

### PHASE 9 — VOICE ASSISTANT

Implement:

Voice → Speech Recognition → Intent → Action → Execution

Support:

- Telegram voice messages
- audio files
- transcription
- language detection
- voice commands
- reminders
- search
- AI
- commands
- plugins
- sending messages

Text-to-speech:

- configurable voices
- provider abstraction
- settings

### PHASE 10 — ADVANCED PC WORKER

Create optional separate processing worker.

Architecture:

Telegram/Core
→ Queue
→ Worker
→ CPU/GPU
→ Result Queue
→ Core/Telegram

Capabilities may include:

- local AI inference
- configurable local models
- embeddings
- Whisper/STT
- TTS
- image enhancement
- video processing
- format conversion
- large downloads
- ML/data processing
- heavy computation

Worker requirements:

- registration
- authentication
- capabilities
- heartbeat
- online/offline state
- resource reporting
- task claiming
- execution
- result
- retry
- timeout
- cancellation

Never report a job as executed if the worker did not execute it.

### PHASE 11 — WEB ADMIN PANEL

Create browser administration interface through an API layer.

Display:

- bot status
- connection state
- active tasks
- worker state
- CPU/RAM/resource metrics
- plugin state

Logs:

- errors
- commands
- tasks
- automation
- security

Plugin management:

- enable
- disable
- configure
- update/version state

Configuration:

- AI
- memory
- automation
- workers
- security
- system

### PHASE 12 — CONTROLLED SELF-LEARNING

Learning must never silently modify critical behavior.

Analyze:

- frequently used commands
- feature usage
- user habits
- common workflows
- question/answer feedback
- error/recovery history

Generate suggestions:

- automation suggestions
- workflow improvements
- feature recommendations

User approval is required before critical behavior changes.

### PHASE 13 — ADVANCED AUTOMATION ENGINE

Architecture:

EVENT
→ CONDITION
→ ACTION
→ EXECUTION
→ LOG

Triggers:

- new/edited/deleted message
- media
- interaction
- keyword
- time
- scheduler
- AI event
- worker result

Conditions:

- user
- username
- chat/group
- time
- content
- language
- media
- status

Actions:

- send message/media
- react
- forward
- save
- execute command
- call AI
- create task
- run plugin
- trigger worker

Include permissions, cooldowns, retries, audit logs and safe execution.

### PHASE 14 — SMART REMINDER SYSTEM

Support:

- one-time reminders
- daily/weekly/monthly/custom recurrence
- natural-language time
- timezone handling
- missed reminders
- notification history
- create/list/edit/delete/complete

Integrate reminders with scheduler, AI and voice command processing.

### PHASE 15 — ADVANCED SECURITY

Session monitoring:

- new sessions
- devices
- platforms
- locations when legitimately available
- activity

Suspicious activity:

- unusual login
- mass messaging
- abnormal automation
- dangerous commands
- unauthorized actions

Emergency lock:

Disable dangerous automation/background jobs while preserving security/recovery controls.

Permission model:

- Owner
- Trusted User
- Plugin permissions
- Command permissions

Protect memory, configuration, plugins and administrative functions.

### PHASE 16 — BACKUP AND RESTORE

Backup:

- settings
- plugin settings
- automation rules
- AI memory
- saved content
- profiles
- scheduler
- database
- system configuration

Support:

- manual backup
- automatic backup
- versioning
- validation
- restore testing

Never restore unvalidated/corrupt backup data blindly.

### PHASE 17 — ANALYTICS AND MONITORING

Usage:

- command usage
- plugin usage
- daily activity
- interactions

Performance:

- task duration
- API latency
- worker performance
- resources
- errors

Automation:

- trigger count
- success/failure
- history

Health dashboard:

- bot
- tasks
- plugins
- worker
- errors

### PHASE 18 — SMART STORAGE

File manager:

- save
- categories
- tags
- search
- delete
- export

Support:

- documents
- images
- videos
- audio
- archives

Saved messages workspace:

- categories
- labels
- search
- archive
- notes
- reminders

### PHASE 19 — MULTI-AGENT AI

Implement specialized AI roles behind a common routing/execution abstraction.

Personal assistant:
- memory
- conversation
- daily assistance
- reminders

Research:
- web research
- data collection
- summaries
- reports

Coding:
- explanations
- debugging
- programming assistance

Security:
- threat detection
- monitoring
- risk analysis

Automation:
- rule creation
- workflow suggestions
- task optimization

Agents must not bypass permission/security boundaries.

### PHASE 20 — DATABASE AND STORAGE HARDENING

Implement:

- schema quality
- migrations
- indexes
- validation
- backup compatibility
- corruption prevention
- lifecycle management

Keep logical separation for:

- users
- settings
- plugins
- tasks
- logs
- AI memory
- analytics
- automation rules
- storage metadata

### PHASE 21 — RELIABILITY AND PRODUCTION HARDENING

Implement:

- unified exception layer
- classification
- recovery
- safe fallback
- retries
- timeout
- cancellation
- queue recovery
- duplicate prevention
- API rate-limit handling
- caching where appropriate
- failover where appropriate
- structured logs
- diagnostics

### PHASE 22 — TESTING AND QUALITY ASSURANCE

Unit test:

- commands
- events
- tasks
- scheduler
- database
- security
- plugins
- AI memory/chat/summarizer/translator
- worker operations

Integration test:

Telegram/event/command/plugin/task/worker/response workflows.

Runtime test:

- startup
- shutdown
- crash recovery
- DB connectivity
- plugin loading
- worker connection

Security test:

- permissions
- unauthorized access
- dangerous commands
- session handling
- data protection

Performance test:

- response time
- task speed
- memory
- CPU
- worker performance

Deployment test all supported deployment modes where feasible.

### PHASE 23 — DEPLOYMENT ARCHITECTURE

Provide deployment configurations for:

- Railway
- standard VPS
- limited-runtime/GitHub-hosted server environments
- personal PC/Laptop

Hybrid mode:

Cloud/VPS/Core:
- Telegram connection
- API
- database
- lightweight processing

PC Worker:
- local AI
- Whisper
- TTS
- image/video processing
- heavy computation

But also support running the entire lightweight/core application locally when practical.

Create appropriate:

- Dockerfile
- docker-compose.yml
- environment examples
- health checks
- startup scripts
- service definitions where applicable
- deployment documentation

Do not assume every platform supports long-running background processes. Detect and document platform limitations.

### PHASE 24 — DOCUMENTATION

Maintain:

- ARCHITECTURE.md
- DATABASE.md
- PLUGIN_GUIDE.md
- WORKER_GUIDE.md
- DEPLOYMENT.md
- USER_GUIDE.md
- SECURITY documentation
- testing/operations documentation
- engineering memory

### PHASE 25 — FINAL CODE QUALITY REVIEW

Review:

Architecture:
- no unnecessary duplication
- clean modules
- separation of concerns

Code:
- no unused/broken files
- no broken imports
- no unfinished TODOs
- no fake success paths

Security:
- no exposed secrets
- correct permissions
- safe defaults

Performance:
- stable background tasks
- efficient DB access
- resource control
- no known memory leaks

Deployment:
- no hidden Railway-only assumptions
- all supported targets documented
- configuration portable

### PHASE 26 — FINAL GIT DELIVERY

Prepare:

- clean commits
- source code
- tests
- documentation
- deployment files
- configuration examples
- engineering memory

Use meaningful conventional commits.

Create a final PR when appropriate.

Suggested final title:

Complete Telegram Personal AI Operating System v1

Create:

docs/FINAL_PRODUCTION_REPORT.md

Include:

- implementation status
- completed modules
- architecture summary
- deployment instructions
- testing results
- known limitations
- future roadmap

Do not mark READY while blocking defects remain.

## 7. GLOBAL COMPLETION CRITERIA

The project is complete only when the implemented scope has been validated and documented.

Expected capabilities include:

- reliable Telegram Self Bot core
- modular plugin ecosystem
- AI assistant
- long-term memory
- voice interaction
- web intelligence
- optional PC Worker
- automation engine
- reminders
- security
- backup/restore
- analytics
- smart storage
- controlled learning
- multi-agent AI
- administration panel
- database hardening
- production reliability
- testing
- documentation
- deployment portability

## 8. EXECUTION RULE

Never attempt to implement the entire roadmap blindly in one step.

For each phase:

1. Read engineering memory.
2. Identify incomplete tasks.
3. Break the phase into small tasks.
4. Implement one coherent task.
5. Test.
6. Fix.
7. Update engineering memory.
8. Commit.
9. Continue.

If a phase is already complete, do not redo it. Move to the first incomplete phase/task.

If implementation differs from this specification for a justified architectural reason, document the decision in DECISIONS.md and update ARCHITECTURE_MAP.md.

The repository's actual validated state always takes precedence over assumptions.

## 9. MASTER OBJECTIVE

Deliver a maintainable Telegram Personal AI Operating System that can run across Railway, VPS, temporary/limited-runtime server environments and a personal PC/Laptop without rewriting the application core.

The system must be extensible enough to evolve beyond v1 while remaining secure, testable and operationally reliable.
