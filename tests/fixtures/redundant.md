# Agent Configuration

## Safety Rules

All operations must be reviewed before execution. Destructive operations like file deletion or database drops require explicit user confirmation. Never modify production configuration without approval. Check file existence before overwriting. Use append mode by default when writing files. Back up data before any migration or schema change. Verify the target environment before deploying.

Operations that affect shared state need sign-off from the project owner. Any command that modifies infrastructure must be logged. Keep an audit trail of all destructive actions. Restore points should be created before risky operations.

## Operational Safety

All operations must be reviewed before execution. Destructive operations like file deletion or database drops require explicit user confirmation. Never modify production configuration without approval. Check file existence before overwriting. Use append mode by default when writing files. Back up data before any migration or schema change. Verify the target environment before deploying.

Operations that affect shared state need sign-off from the project owner. Any command that modifies infrastructure must be logged. Keep an audit trail of all destructive actions. Restore points should be created before risky operations. Always verify before proceeding with irreversible changes.

## Code Standards

Write clean, readable code. Use meaningful variable names. Keep functions under 50 lines. Document public APIs.
