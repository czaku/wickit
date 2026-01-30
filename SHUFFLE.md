# wickit.shuffle - Port Management & Service Discovery

Auto-discover available ports, register mDNS services, and enable frontend-backend service discovery for multi-tool architectures.

## Features

- 🔍 **Port Discovery**: Automatically find available ports in a specified range
- 🌐 **mDNS Registration**: Register services as `*.local` domains (macOS/Bonjour)
- 🏥 **Health Endpoints**: Standardized health check responses
- 🔗 **Service Discovery**: Frontend auto-discovers backend via health checks
- 🎯 **Multi-Tool Support**: Each tool gets its own port ranges to avoid conflicts

## Installation

Wickit includes both Python and TypeScript/JavaScript modules:

```bash
# Python (included in wickit)
pip install wickit

# TypeScript (use directly from repo, no npm package needed)
# Just import from wickit-js/shuffle.ts
```

## Usage

### Python Backend (Flask Example)

```python
from flask import Flask
from wickit.shuffle import ServiceRegistry

app = Flask(__name__)

# Auto-discover port and register mDNS
registry = ServiceRegistry(
    service_id="ralfie-api",
    port_range=(7770, 7779),
    mdns_name="ralfie.local",
    metadata={
        "version": "0.1.0",
        "frontend_ports": (5170, 5179)
    }
)

port = registry.start()

# Add health endpoint
@app.route('/api/health')
def health():
    return registry.health_response()

# Run on discovered port
if __name__ == '__main__':
    app.run(port=port)
```

### TypeScript Frontend (Vite Example)

```typescript
import { discoverService } from '@/path/to/wickit-js/shuffle';

// Auto-discover backend on startup
async function initApp() {
    try {
        const backend = await discoverService({
            serviceId: 'ralfie-api',
            portRange: [7770, 7779],
            timeout: 5000
        });

        console.log(`✅ Backend discovered: ${backend.url}`);
        console.log(`📊 Health:`, backend.health);

        // Use backend.url for API calls
        const data = await fetch(`${backend.url}/api/data`);

    } catch (error) {
        console.error('❌ Backend not found:', error);
    }
}

initApp();
```

### Vite Config with Auto-Discovery

```typescript
import { defineConfig } from 'vite';
import { createAutoDiscoveryProxy } from '@/path/to/wickit-js/shuffle';

export default defineConfig(async () => {
    // Discover backend at build time
    const backendUrl = await createAutoDiscoveryProxy({
        serviceId: 'ralfie-api',
        portRange: [7770, 7779]
    });

    return {
        server: {
            proxy: {
                '/api': {
                    target: backendUrl,
                    changeOrigin: true
                }
            }
        }
    };
});
```

## Port Allocation Strategy

Recommended port ranges for multiple tools:

```python
# Example: Multiple tools with non-overlapping ranges
TOOLS_CONFIG = {
    'ralfie': {
        'api_ports': (7770, 7779),
        'frontend_ports': (5170, 5179)
    },
    'pretzel': {
        'api_ports': (7780, 7789),
        'frontend_ports': (5180, 5189)
    },
    'another-tool': {
        'api_ports': (7790, 7799),
        'frontend_ports': (5190, 5199)
    }
}
```

## Health Endpoint Response Format

Standard health check response:

```json
{
    "service": "ralfie-api",
    "status": "healthy",
    "port": 7777,
    "mdns": "ralfie.local",
    "uptime_seconds": 123.45,
    "metadata": {
        "version": "0.1.0",
        "frontend_ports": [5170, 5179]
    }
}
```

## API Reference

### Python

#### `ServiceRegistry`

Main class for service registration and management.

**Constructor:**
```python
ServiceRegistry(
    service_id: str,
    port_range: Tuple[int, int],
    mdns_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

**Methods:**
- `start(preferred_port: Optional[int] = None) -> int`: Start service, returns port
- `health_response() -> Dict[str, Any]`: Generate health check response
- `stop()`: Cleanup and unregister mDNS

#### `find_available_port`

```python
find_available_port(port_range: Tuple[int, int]) -> int
```

Find first available port in range.

#### `quick_start`

```python
quick_start(
    service_id: str,
    port_range: Tuple[int, int],
    mdns_name: Optional[str] = None
) -> int
```

Convenience function for simple use cases.

### TypeScript

#### `discoverService`

```typescript
async function discoverService(
    options: DiscoverOptions
): Promise<DiscoveredService>
```

Discover backend service by scanning ports and checking health endpoints.

#### `discoverServiceWithRetry`

```typescript
async function discoverServiceWithRetry(
    options: DiscoverOptions,
    maxRetries: number = 3,
    initialDelay: number = 1000
): Promise<DiscoveredService>
```

Discover service with exponential backoff retries.

## Examples

### Flask with Tauri Desktop App

**Backend (Python):**
```python
from flask import Flask
from wickit.shuffle import ServiceRegistry

registry = ServiceRegistry(
    service_id="my-app-api",
    port_range=(7770, 7779),
    mdns_name="myapp.local"
)

app = Flask(__name__)
port = registry.start()

@app.route('/api/health')
def health():
    return registry.health_response()

app.run(port=port)
```

**Frontend (TypeScript/React):**
```typescript
import { discoverService } from '@/wickit-js/shuffle';

// On app startup
const backend = await discoverService({
    serviceId: 'my-app-api',
    portRange: [7770, 7779]
});

// Use backend.url for all API calls
fetch(`${backend.url}/api/data`);
```

## Requirements

- Python 3.8+
- `zeroconf` package for mDNS (optional but recommended)

```bash
pip install zeroconf
```

## License

Same as wickit library.
