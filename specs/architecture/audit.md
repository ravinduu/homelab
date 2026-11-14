# Audit and observability

Current gateway and approval helper emit fixed authpriv syslog events with
caller label, operation, service, and result. Approval contents, environment,
Docker output, and exception text are excluded. Status returns the inventory
output. Tests exercise gateway paths.

Target events should include correlation ID, verified principal, credential
reference (not secret), operation/resource, policy revision, decision/reason,
approval reference, adapter result, times, and integrity/forwarding status.
Do not log secrets or unbounded output. Define retention, access, time
synchronization, forwarding, tamper detection, and disk-full behavior before
claiming durable auditability. Root compromise can alter local logs;
append-only remote collection is future work.
