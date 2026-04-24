# API Contract: Consult Endpoint

**Version**: 1.0.0  
**Date**: 2026-04-24  
**Feature**: 001-ai-engine-initialization  
**Status**: Proposed (not yet implemented)

## Overview

This contract defines the HTTP API for the `/api/v1/ai/consult` endpoint, which is the entry point for consultation requests from the NestJS server (`interasisai-server`) to the FastAPI AI engine.

---

## Endpoint Specification

### POST /api/v1/ai/consult

**Purpose**: Process a consultation request and return an echo response (MVP)  
**Protocol**: HTTP/1.1 or HTTP/2  
**Authentication**: Internal header-based (`X-Internal-Secret`)  
**Rate Limiting**: None (MVP)  
**Timeout**: 30 seconds (FastAPI default)

---

## Request

### HTTP Headers (Required)

| Header | Type | Value | Description |
|--------|------|-------|-------------|
| `Content-Type` | string | `application/json` | Request body format |
| `X-Internal-Secret` | string | Secret key | Internal authentication token |

**Header Validation**:
- `X-Internal-Secret` MUST be present
- `X-Internal-Secret` MUST match `X_INTERNAL_SECRET` environment variable
- If missing or incorrect: return 403 Forbidden (see Response section)
- Header comparison is case-sensitive

### HTTP Body

**Format**: JSON  
**Encoding**: UTF-8

**Schema**:
```json
{
  "message": "string (required, 1-2000 characters)"
}
```

**Field Definitions**:

| Field | Type | Required | Min | Max | Description |
|-------|------|----------|-----|-----|-------------|
| `message` | string | YES | 1 | 2000 | Consultation query for the LLM (future) or echo (MVP) |

**Validation**:
- `message` MUST NOT be empty (min_length=1)
- `message` MUST NOT exceed 2000 characters (max_length=2000)
- Validation happens at Pydantic schema layer (automatic 422 response on failure)

### Request Examples

**Valid Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: my-secret-key" \
  -d '{"message": "What is 2+2?"}'
```

**Invalid: Missing X-Internal-Secret Header**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?"}'
# Response: 403 Forbidden
```

**Invalid: Empty Message**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: my-secret-key" \
  -d '{"message": ""}'
# Response: 422 Unprocessable Entity
```

**Invalid: Message Too Long**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -H "X-Internal-Secret: my-secret-key" \
  -d '{"message": "' + 'x' * 2001 + '"}'
# Response: 422 Unprocessable Entity
```

---

## Response

### 200 OK (Success)

**Format**: JSON  
**Encoding**: UTF-8

**Schema**:
```json
{
  "message": "string",
  "timestamp": "string (ISO 8601 datetime)"
}
```

**Field Definitions**:

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Echoed from request (MVP); future: LLM response |
| `timestamp` | string | ISO 8601 datetime in UTC (e.g., "2026-04-24T12:34:56.789Z") |

**Example Response**:
```json
{
  "message": "What is 2+2?",
  "timestamp": "2026-04-24T12:34:56.789123Z"
}
```

**Response Headers**:
- `Content-Type: application/json; charset=utf-8`
- `X-Powered-By: FastAPI` (optional)

---

### 403 Forbidden (Authentication Failure)

**When**: `X-Internal-Secret` header is missing or incorrect

**Format**: JSON  
**Encoding**: UTF-8

**Schema**:
```json
{
  "detail": "Forbidden"
}
```

**Notes**:
- No body details provided (prevent information leakage)
- Same response for missing vs. incorrect secret (no discrimination)
- Middleware returns this; route handler never executes

**Example Response**:
```json
{
  "detail": "Forbidden"
}
```

---

### 422 Unprocessable Entity (Validation Failure)

**When**: Request body validation fails (e.g., empty message, message too long)

**Format**: JSON  
**Encoding**: UTF-8

**Schema**:
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Notes**:
- FastAPI automatically generates this response from Pydantic validation
- Provides developers with clear error details
- Client should re-validate before retrying

**Example Response** (empty message):
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

### 500 Internal Server Error (Unexpected Failure)

**When**: Server encounters an unexpected error during processing

**Format**: JSON  
**Encoding**: UTF-8

**Schema**:
```json
{
  "detail": "Internal server error"
}
```

**Notes**:
- Should rarely occur in MVP (only business logic is echo)
- Full exception details logged server-side (never returned to client)
- Client should implement retry logic with exponential backoff

---

## HTTP Status Code Summary

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Success: message echoed | ConsultResponse JSON |
| 403 | Auth failure: wrong/missing secret | `{"detail": "Forbidden"}` |
| 422 | Validation failure: invalid message | Error details from Pydantic |
| 500 | Server error | `{"detail": "Internal server error"}` |

---

## Backward Compatibility

**Version**: 1.0.0 (first version)  
**Breaking Change Policy**: None yet (MVP has no prior versions)

**Future Versioning**:
- If response fields are added: version changes to 1.1.0 (minor)
- If response fields are removed: version changes to 2.0.0 (major)
- If request fields are added (optional): version stays 1.x (backward compatible)
- If request fields are added (required): version changes to 2.0.0 (major)

---

## Security Considerations

### Authentication

- **Mechanism**: Header-based shared secret (`X-Internal-Secret`)
- **Transport**: HTTPS in production (enforced at infra level, not this service)
- **Secret Length**: Recommended ≥32 characters (documented)
- **Secret Rotation**: External policy (future work)

### Authorization

- **Model**: Binary (authenticated vs. not authenticated)
- **Future**: Role-based access control (future phases)

### Input Validation

- **Message Length**: Limited to 2000 characters (DoS protection)
- **JSON Schema**: Validated by Pydantic (prevents injection)
- **No Deserialization of Untrusted Code**: JSON only (safe)

### Error Handling

- **No Information Leakage**: 403 doesn't reveal why auth failed
- **Logging**: Failures logged server-side for monitoring (never returned to client)
- **Stack Traces**: Never exposed to clients

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| p50 latency | <10ms | Echo processing only |
| p95 latency | <100ms | Includes network jitter |
| p99 latency | <500ms | Still acceptable for MVP |
| Throughput | 100+ req/s | Single instance baseline |
| Concurrent connections | 100+ | Uvicorn default |

---

## Testing Checklist

- [ ] Happy path: valid request → 200 + echoed message
- [ ] Missing X-Internal-Secret header → 403
- [ ] Incorrect X-Internal-Secret header → 403
- [ ] Empty message → 422 Unprocessable Entity
- [ ] Message > 2000 chars → 422 Unprocessable Entity
- [ ] Concurrent requests all validated independently
- [ ] Timestamp is UTC and ISO 8601 formatted
- [ ] Content-Type header is correct
- [ ] 403 response body identical for missing vs. incorrect secret

---

## OpenAPI Documentation

This endpoint will be automatically documented in OpenAPI 3.0 format by FastAPI:
- **URL**: http://localhost:8000/docs (Swagger UI)
- **URL**: http://localhost:8000/redoc (ReDoc)
- **JSON**: http://localhost:8000/openapi.json

The OpenAPI spec will be auto-generated from Pydantic schemas and route definitions.

---

**Status**: ✅ Proposed  
**Review**: Ready for implementation review  
**Implementation**: Use this contract as guide for `presentation/routes/consult_routes.py`
