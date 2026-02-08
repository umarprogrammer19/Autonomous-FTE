# WhatsApp Automation System API Documentation

## Overview

The WhatsApp Automation System uses the whapi.cloud HTTP API to send and receive messages. This document describes how to interact with the system and use its features.

## Environment Variables

All configurations are managed through environment variables:

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WHAPI_TOKEN` | Yes | Your whapi.cloud API token | N/A |
| `WHAPI_BASE_URL` | No | Base URL for whapi.cloud API | https://gate.whapi.cloud |
| `WEBHOOK_PORT` | No | Port for webhook server | 8000 |
| `POLLING_INTERVAL` | No | Polling interval in seconds | 30 |
| `USE_WEBHOOK` | No | Enable webhook mode | false |

## System Architecture

### Message Processing Flow

1. **Message Reception**:
   - **Polling Mode**: System periodically fetches messages from whapi.cloud API
   - **Webhook Mode**: whapi.cloud sends real-time notifications to your server

2. **AI Detection**: Messages are analyzed against a list of AI-related keywords

3. **Response Generation**: AI-related messages trigger Claude-like response generation

4. **Message Sending**: Responses are sent back using whapi.cloud API

### Core Components

- `WhatsAppAutomation`: Main class managing the automation system
- `manual_send_message()`: Function for sending manual messages
- Message processing pipeline: Handles detection, generation, and response

## API Endpoints Used

The system interacts with the following whapi.cloud API endpoints:

### Sending Messages
```
POST https://gate.whapi.cloud/messages/text
```

### Receiving Messages
```
GET https://gate.whapi.cloud/messages
```
*Note: Actual endpoint may vary based on whapi.cloud's API documentation*

## Keyword Detection

The system identifies AI-related messages using these keywords (case-insensitive):

### General AI Terms
- `ai`, `artificial intelligence`
- `chatgpt`, `llm`, `large language model`
- `ml`, `machine learning`
- `gpt`, `openai`, `anthropic`, `claude`

### Programming & Development
- `python`, `javascript`
- `programming`, `coding`, `software`, `development`
- `algorithm`, `data science`, `analytics`

### Advanced AI Concepts
- `neural network`, `deep learning`
- `nlp`, `natural language processing`
- `computer vision`, `robotics`
- `automation`, `agents`

## Usage Examples

### Starting the System

#### Polling Mode (Default)
```bash
# With environment variables set
python whatsapp_automation.py
```

#### Webhook Mode
```bash
# Set USE_WEBHOOK=true in .env or as environment variable
export USE_WEBHOOK=true
python whatsapp_automation.py
```

### Command Line Interface

#### Send a Message
```bash
python whatsapp_cli.py send 923182710120 "Hello from automation!"
```

#### Start the System
```bash
python whatsapp_cli.py start
# Or with webhook mode
python whatsapp_cli.py start --webhook
```

#### Create Sample Config
```bash
python whatsapp_cli.py config --create-sample
```

### Programmatic Usage

#### Send Manual Message
```python
from whatsapp_automation import manual_send_message

success = manual_send_message("923182710120", "Hello World!")
if success:
    print("Message sent successfully")
```

#### Initialize Custom Automation
```python
from whatsapp_automation import WhatsAppAutomation
import os

# Set environment variable
os.environ['WHAPI_TOKEN'] = 'your_token_here'

wa = WhatsAppAutomation()
# Customize AI keywords if needed
wa.ai_keywords.extend(['custom', 'keywords'])

# Send a message
wa.send_whatsapp_message("923182710120", "Custom message")
```

## Response Generation Logic

The system uses different response templates based on message content:

### Python-Specific Responses
Messages containing "python" trigger Python-focused AI responses about libraries like TensorFlow, PyTorch, etc.

### JavaScript-Specific Responses
Messages with "javascript" get web development-focused AI responses.

### Platform-Specific Responses
Mentions of "chatgpt", "gpt", or "openai" trigger comparative responses about Claude and AI safety.

### General AI Responses
Default template for general AI-related messages.

## Error Handling

The system logs all errors to `whatsapp_automation.log` with timestamps and error details.

### Common Issues

1. **Authentication Errors**: Check `WHAPI_TOKEN` validity
2. **Network Errors**: Verify internet connectivity and API endpoint accessibility
3. **Rate Limiting**: whapi.cloud may have rate limits; adjust `POLLING_INTERVAL` if needed
4. **Invalid Phone Numbers**: Ensure phone numbers are in correct international format

## Security Best Practices

1. **Token Security**: Never commit `WHAPI_TOKEN` to version control
2. **HTTPS**: Use HTTPS for webhook endpoints in production
3. **Input Validation**: The system validates message content before processing
4. **Logging**: Sensitive information is not logged

## Testing

Run the test suite to verify functionality:
```bash
python test_whatsapp_automation.py
# Or using CLI
python whatsapp_cli.py test
```

## Docker Deployment

Build and run using Docker:
```bash
# Build the image
docker build -t whatsapp-automation .

# Run with environment variables
docker run -d \
  -e WHAPI_TOKEN=your_token_here \
  -e USE_WEBHOOK=true \
  -p 8000:8000 \
  whatsapp-automation
```

## Troubleshooting

### Debugging Steps

1. Check logs in `whatsapp_automation.log`
2. Verify whapi.cloud connection status
3. Confirm phone number format
4. Test API token validity
5. Check firewall/network restrictions

### Monitoring

The system logs:
- Incoming messages and processing status
- Outgoing message attempts and results
- API request/response details
- Error conditions and exceptions