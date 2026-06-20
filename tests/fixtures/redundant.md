# Agent Configuration

## Safety Rules

All operations must be reviewed before execution. Destructive operations like file deletion or database drops require explicit user confirmation. Never modify production configuration without approval. Check file existence before overwriting. Use append mode by default when writing files. Back up data before any migration or schema change. Verify the target environment before deploying.

Operations that affect shared state need sign-off from the project owner. Any command that modifies infrastructure must be logged. Keep an audit trail of all destructive actions. Restore points should be created before risky operations.

## Operational Safety

Every operation requires review prior to execution. Destructive actions such as deleting files or dropping database tables need explicit confirmation from the user. Production configuration must never be changed without prior approval. Always verify that files exist before overwriting them. Default to append mode for file writes. Create backups before performing migrations or schema changes. Confirm the deployment target environment beforehand.

Changes to shared state require approval from the project owner. Infrastructure-modifying commands must be logged. Maintain an audit trail for all destructive operations. Create restore points before performing high-risk operations.

## Code Standards

Write clean, readable code. Use meaningful variable names. Keep functions under 50 lines. Document public APIs.
