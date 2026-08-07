# Wiki Log

Append-only history of writes to the shared wiki. Only `ingest` and `lint` write
here — `query` and `status` are read-only and never add an entry.

Ingest entries:

```text
## [YYYY-MM-DD] ingest | <title> | <source-path>
```

Lint entries, followed by the payload line:

```text
## [YYYY-MM-DD] lint | <scope> | <summary>
missing-pages: <comma-list or none> · mechanical-fixes: <N>
```
