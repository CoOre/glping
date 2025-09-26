# GitLab Ping Architecture

## Overview

GitLab Ping is a Python-based CLI utility that monitors GitLab events and delivers desktop notifications in real-time. The architecture is designed to be modular, extensible, and cross-platform compatible.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitLab API    │◄──►│  GitLab Ping    │◄──►│ Desktop Notifier│
│                 │    │                 │    │                 │
│ • Events        │    │ • Core Logic    │    │ • Windows       │
│ • Projects      │    │ • Cache System  │    │ • macOS         │
│ • Users         │    │ • Config Mgmt   │    │ • Linux         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   Web Dashboard │
                       │                 │
                       │ • SSE Events    │
                       │ • Real-time UI  │
                       │ • Event History │
                       └─────────────────┘
```

## Core Components

### 1. Main Application (`glping/main.py`)
- **Purpose**: Entry point and CLI interface
- **Responsibilities**:
  - Parse command-line arguments
  - Initialize configuration
  - Start monitoring process
  - Handle daemon mode
  - Manage application lifecycle

### 2. GitLab Client (`glping/gitlab_client.py`)
- **Purpose**: Interface with GitLab API
- **Responsibilities**:
  - API authentication and requests
  - Event fetching and pagination
  - Rate limiting handling
  - Error recovery and retries
  - Data normalization

### 3. Event Processor (`glping/event_processor.py`)
- **Purpose**: Process and filter GitLab events
- **Responsibilities**:
  - Event type filtering
  - Event deduplication
  - Event enrichment
  - Priority assignment
  - Event routing

### 4. Notification System (`glping/notifier.py`)
- **Purpose**: Cross-platform desktop notifications
- **Responsibilities**:
  - Platform-specific notification delivery
  - Notification grouping and stacking
  - Sound and visual effects
  - Notification persistence
  - User interaction handling

### 5. Cache Manager (`glping/cache.py`)
- **Purpose**: Unified caching system
- **Responsibilities**:
  - Event deduplication
  - Persistent storage (`glping_cache.json`)
  - Cache expiration and cleanup
  - Performance optimization
  - Data integrity

### 6. Configuration Manager (`glping/config.py`)
- **Purpose**: Application configuration
- **Responsibilities**:
  - Config file parsing and validation
  - Environment variable handling
  - Default value management
  - Configuration schema validation
  - Runtime configuration updates

### 7. Web Dashboard (`glping/web/`)
- **Purpose**: Real-time web interface
- **Components**:
  - `dashboard.py`: Web server and SSE endpoints
  - `static/`: Frontend assets (HTML, CSS, JS)
  - `templates/`: Jinja2 templates
- **Features**:
  - Real-time event streaming
  - Event history and search
  - Configuration management
  - System status monitoring

## Data Flow

```
GitLab API → GitLab Client → Event Processor → Cache Manager → Notifier
     ↓                                                              ↓
Web Dashboard ← SSE Server ← Event Processor ← Cache Manager ← User Interaction
```

### Event Processing Pipeline

1. **Event Fetching**: GitLab Client polls GitLab API for new events
2. **Event Filtering**: Event Processor filters based on configuration
3. **Deduplication**: Cache Manager checks for duplicate events
4. **Notification**: Notifier delivers desktop notifications
5. **Web Streaming**: SSE Server streams events to web dashboard
6. **Persistence**: Cache Manager stores events for history

## Key Design Patterns

### 1. Observer Pattern
- **Usage**: Event notification system
- **Components**: Event producers and consumers
- **Benefits**: Loose coupling, extensibility

### 2. Strategy Pattern
- **Usage**: Platform-specific notification handlers
- **Components**: Notifier implementations for each OS
- **Benefits**: Platform abstraction, easy extension

### 3. Factory Pattern
- **Usage**: Event and notification creation
- **Components**: Event and notification factories
- **Benefits**: Centralized creation logic, consistency

### 4. Singleton Pattern
- **Usage**: Configuration and cache management
- **Components**: Config and Cache managers
- **Benefits**: Single source of truth, resource efficiency

## Configuration Architecture

### Configuration Sources (Priority Order)
1. Command-line arguments (highest)
2. Environment variables
3. Configuration file (`config.yaml`)
4. Default values (lowest)

### Configuration Schema
```yaml
gitlab:
  url: "https://gitlab.com"
  token: "personal_access_token"
  projects: []  # Empty means all projects

monitoring:
  events:
    - push
    - merge_request
    - issue
    - pipeline
    - comment
  interval: 30  # seconds
  max_events: 100

notifications:
  enabled: true
  sound: true
  duration: 5000  # milliseconds
  grouping: true

cache:
  enabled: true
  file: "glping_cache.json"
  max_size: 10000
  ttl: 86400  # 24 hours

web:
  enabled: true
  port: 8080
  host: "localhost"
```

## Notification System Architecture

### Platform-Specific Implementations

#### Windows
- **Technology**: Windows Toast Notifications
- **Features**: Action buttons, progress bars, images
- **Library**: `win10toast`

#### macOS
- **Technology**: macOS Notification Center
- **Features**: Grouping, stacking, sounds
- **Library**: `pyobjc`

#### Linux
- **Technology**: D-Bus Notifications
- **Features**: Standard desktop notifications
- **Library**: `dbus`

### Notification Grouping
- **Strategy**: Unique groups per event type
- **Implementation**: `glping-{notification_id[:8]}`
- **Benefits**: Prevents overlapping, improves organization

## Cache Architecture

### Cache Structure
```json
{
  "version": "1.0",
  "events": {
    "event_id": {
      "id": "event_id",
      "type": "push",
      "project_id": 123,
      "created_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:00:01Z",
      "notified": true
    }
  },
  "metadata": {
    "last_update": "2024-01-01T00:00:01Z",
    "total_events": 1000,
    "cache_size": 1024
  }
}
```

### Cache Operations
- **Read**: Check for existing events
- **Write**: Store new events
- **Update**: Modify event status
- **Cleanup**: Remove expired events
- **Compact**: Optimize storage

## Web Dashboard Architecture

### Frontend Components
- **Event List**: Real-time event display
- **Event Details**: Detailed event information
- **Configuration UI**: Settings management
- **System Status**: Health and performance metrics

### Backend Components
- **SSE Server**: Real-time event streaming
- **REST API**: Configuration and data access
- **Static File Server**: Asset delivery
- **Authentication**: Basic auth protection

### SSE Event Format
```json
{
  "type": "event",
  "data": {
    "id": "event_id",
    "type": "push",
    "project": {
      "id": 123,
      "name": "project_name"
    },
    "author": {
      "name": "author_name",
      "username": "author_username"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "message": "Event description"
  }
}
```

## Error Handling Architecture

### Error Types
1. **Network Errors**: API connectivity issues
2. **Authentication Errors**: Invalid tokens or permissions
3. **Configuration Errors**: Invalid config files
4. **Platform Errors**: OS-specific notification issues
5. **Cache Errors**: Storage or corruption issues

### Error Handling Strategy
- **Retry**: Transient errors with exponential backoff
- **Fallback**: Alternative notification methods
- **Logging**: Comprehensive error logging
- **User Notification**: Clear error messages
- **Graceful Degradation**: Continue with limited functionality

## Performance Considerations

### Optimization Strategies
1. **Caching**: Reduce API calls and duplicate processing
2. **Async Processing**: Non-blocking event handling
3. **Batch Processing**: Process multiple events together
4. **Memory Management**: Efficient data structures
5. **Connection Pooling**: Reuse API connections

### Resource Usage
- **Memory**: Minimal footprint with efficient caching
- **CPU**: Low usage with async processing
- **Network**: Optimized API calls with pagination
- **Storage**: Efficient cache file format

## Security Architecture

### Data Protection
- **Token Security**: Secure storage and transmission
- **Configuration Protection**: Encrypted sensitive data
- **Network Security**: HTTPS for all communications
- **Access Control**: Minimal required permissions

### Security Best Practices
- **Token Rotation**: Regular token updates
- **Rate Limiting**: Respect API limits
- **Input Validation**: Sanitize all inputs
- **Error Information**: Avoid sensitive data exposure

## Extensibility

### Plugin Architecture
- **Event Plugins**: Custom event processors
- **Notification Plugins**: New notification platforms
- **Storage Plugins**: Alternative cache backends
- **Integration Plugins**: Third-party service integrations

### Extension Points
1. **Event Types**: Add new GitLab event types
2. **Notification Channels**: Support new platforms
3. **Storage Backends**: Alternative cache storage
4. **Authentication Methods**: Additional auth providers

## Monitoring and Observability

### Metrics Collection
- **Event Processing Rate**: Events processed per second
- **Notification Success Rate**: Successful notifications
- **API Response Time**: GitLab API performance
- **Cache Hit Rate**: Cache effectiveness
- **Error Rate**: Error frequency and types

### Logging
- **Structured Logging**: JSON format for machine readability
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Automatic log file management
- **Contextual Information**: Request and event correlation

---

This architecture document provides a comprehensive overview of GitLab Ping's design and implementation. For more detailed information about specific components, please refer to the source code documentation.