# webhook-relay-service

[![Build](https://github.com/Retsumdk/webhook-relay-service/workflows/Test/badge.svg)](https://github.com/Retsumdk/webhook-relay-service/actions)
[![TypeScript](https://img.shields.io/badge/typescript-4.9-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18-brightgreen.svg)](https://nodejs.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Universal webhook relay with retry logic and transformations. A production-ready service for routing, transforming, and retrying webhooks.

## Features

- **Universal webhook relay** - Receive webhooks and forward to multiple destinations
- **Retry logic** - Automatic retries with exponential backoff
- **Payload transformations** - Transform webhook payloads with JSONata
- **Event filtering** - Filter events based on rules
- **Signature verification** - Verify webhook signatures (GitHub, Stripe, etc.)
- **Dead letter queue** - Handle failed deliveries

## Installation

```bash
npm install webhook-relay-service
# or
pnpm add webhook-relay-service
```

## Quick Start

```typescript
import { WebhookRelayService } from 'webhook-relay-service';

const relay = new WebhookRelayService({
  port: 3000,
  endpoints: [
    {
      path: '/webhook',
      target: 'https://your-api.com/webhook',
      retryAttempts: 3,
      transform: 'payload.data = $.event.body',
    }
  ]
});

relay.start();
```

## Configuration

```typescript
{
  port: number;                    // Server port
  endpoints: Endpoint[];            // List of relay endpoints
  deadLetterQueue?: boolean;        // Enable DLQ (default: true)
  signatureSecret?: string;         // For signature verification
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built by [Retsumdk](https://github.com/Retsumdk)
