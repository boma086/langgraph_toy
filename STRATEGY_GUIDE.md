# Strategy Selection System

## Overview

The LangGraph toy project now supports configurable execution strategy selection through a multi-level decision system. This allows you to choose between traditional and compiled execution strategies without modifying code.

## Strategy Types

### 1. Traditional Strategy
- Creates a new graph for each execution
- No caching overhead
- Better for simple, one-off requests
- Strategy key: `traditional`

### 2. Compiled Strategy
- Caches and reuses graphs for better performance
- Ideal for repeated requests with the same agent
- Slightly higher memory usage
- Strategy key: `compiled`

### 3. Auto Strategy
- Automatically selects based on request complexity
- Uses compiled for complex requests, traditional for simple ones
- Strategy key: `auto`

## Multi-Level Decision System

The strategy selection follows this priority order:

1. **Request Level** - Explicit strategy in request body
2. **Header Level** - Strategy specified in HTTP header
3. **Auto Selection** - Based on request complexity (if enabled)
4. **Environment Default** - Configured default strategy

## Usage Examples

### 1. Via Request Body
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 2+2?",
    "agent_type": "simple",
    "strategy": "compiled"
  }'
```

### 2. Via HTTP Header
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-Execution-Strategy: compiled" \
  -d '{
    "message": "What is 2+2?",
    "agent_type": "simple"
  }'
```

### 3. Environment Configuration
```bash
# Set default strategy
export DEFAULT_STRATEGY=compiled

# Enable auto-switching
export AUTO_STRATEGY=true

# Start server
python main.py
```

## Configuration

### Environment Variables

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `DEFAULT_STRATEGY` | Default execution strategy | `traditional` | `traditional`, `compiled`, `auto` |
| `AUTO_STRATEGY` | Enable automatic strategy switching | `false` | `true`, `false` |
| `COMPILED_CACHE_SIZE` | Cache size for compiled strategy | `50` | Any positive integer |
| `COMPLEXITY_THRESHOLD` | Threshold for auto-switching | `7` | 1-10 |

### Response Format

The API response now includes strategy information:

```json
{
    "response": "I've used some tools to help answer your question. Tool result: 4.0",
    "agent_type": "simple",
    "timestamp": 1757512799.189229,
    "strategy_used": "compiled",
    "execution_stats": {
        "execution_time": 0.04020977020263672,
        "cache_hits": 0,
        "cache_misses": 1,
        "hit_rate": 0.0
    }
}
```

## Performance Considerations

### When to Use Traditional Strategy
- Simple, one-off requests
- Debugging and development
- Memory-constrained environments
- Requests that don't benefit from caching

### When to Use Compiled Strategy
- Repeated requests with the same agent
- High-traffic production environments
- Complex calculations or reasoning
- When performance is critical

### When to Use Auto Strategy
- Mixed workload environments
- When you want automatic optimization
- Development and testing scenarios
- When request patterns vary significantly

## Monitoring and Logging

The system provides detailed logging for strategy selection decisions:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Strategy selection logs
logger.info(f"Strategy selected: {strategy_type} for request {request_id}")

# Performance metrics
logger.info(f"Execution stats: {execution_stats}")
```

## Testing

### Test Different Strategies
```bash
# Test traditional strategy
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "agent_type": "simple", "strategy": "traditional"}'

# Test compiled strategy
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "agent_type": "simple", "strategy": "compiled"}'

# Test header-based selection
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-Execution-Strategy: compiled" \
  -d '{"message": "Hello", "agent_type": "simple"}'
```

## Migration Guide

### From Hard-coded Traditional Strategy
No changes needed - the system defaults to traditional strategy.

### From Hard-coded Compiled Strategy
Set the environment variable:
```bash
export DEFAULT_STRATEGY=compiled
```

### For New Development
Consider using the auto strategy for automatic optimization:
```bash
export DEFAULT_STRATEGY=auto
export AUTO_STRATEGY=true
```

## Best Practices

1. **Development Environment**: Use traditional strategy for easier debugging
2. **Production Environment**: Use compiled strategy for better performance
3. **Testing Environment**: Use auto strategy for comprehensive testing
4. **Monitor Performance**: Use the execution stats to optimize strategy selection
5. **Configure Appropriately**: Set complexity thresholds based on your workload

## Troubleshooting

### Common Issues

1. **Strategy Not Applied**
   - Check environment variables are set correctly
   - Verify request body/header format
   - Check logs for strategy selection decisions

2. **Performance Issues**
   - Monitor cache hit/miss rates
   - Adjust complexity thresholds
   - Consider increasing cache size for compiled strategy

3. **Memory Usage**
   - Monitor cache size and memory usage
   - Consider using traditional strategy for memory-constrained environments
   - Adjust `COMPILED_CACHE_SIZE` as needed