# Brand Persona Onboarding System

## Overview

The Brand Persona Onboarding system allows each user/brand to create a comprehensive persona document that captures their unique voice, tone, writing style, and preferences. This persona is then used to generate content that perfectly matches the brand's identity.

Based on the methodology from: [I am just a text file - Ruben Hassid](https://open.substack.com/pub/ruben/p/i-am-just-a-text-file)

## How It Works

### 1. Interview Process

Users go through a 100-question interview conducted by Claude AI, covering:

- **Beliefs & Contrarian Takes** (15 questions)
- **Writing Mechanics** (20 questions)
- **Aesthetic Crimes** (15 questions)
- **Voice & Personality** (15 questions)
- **Structural Preferences** (15 questions)
- **Hard Nos** (10 questions)
- **Red Flags** (10 questions)

### 2. Key Principles

- **Focus on Rejections**: 80% of the persona captures what the brand would NEVER say or do
- **Be Specific**: Instead of "I like clarity," users are pushed to say "I never use 'leverage' as a verb, I keep paragraphs under 3 sentences"
- **Natural Flow**: The interview adapts based on interesting threads that emerge

### 3. Persona Document

After completing the interview, a comprehensive markdown document is generated that includes:

- Complete answers to all 100 questions
- Quick reference card (Always/Never lists)
- Signature phrases and structures
- Voice calibration guidelines
- Anti-overfitting guide (to prevent rigid application)

## Usage

### Starting Onboarding

1. Navigate to `/onboarding`
2. Select a project/client
3. Click "Start Interview"
4. Answer questions one by one (can skip if needed)
5. Review the generated persona document
6. Save to activate for all content generation

### Accessing the Onboarding

- **URL**: `/onboarding`
- **Authentication**: Required (must be logged in)
- **Access Control**: Users can only onboard projects they have access to

## API Endpoints

### Start Interview
```
POST /api/onboarding/<client_id>/start
```
Creates a new interview session and returns a `session_id`.

### Get Next Question
```
GET /api/onboarding/<client_id>/question?session_id=<session_id>
```
Returns the next question in the interview. Returns `{"complete": true}` when all 100 questions are done.

### Submit Answer
```
POST /api/onboarding/<client_id>/answer
Body: {
  "session_id": "<session_id>",
  "answer": "<user's answer>"
}
```
Submits an answer to the current question.

### Complete Interview
```
GET /api/onboarding/<client_id>/complete?session_id=<session_id>
```
Generates the final persona document from all answers.

### Save Persona
```
POST /api/onboarding/<client_id>/save
Body: {
  "persona": "<markdown persona document>"
}
```
Saves the persona document to `brand.persona` in the client configuration.

## Storage

The persona document is stored in:
- **Supabase**: `clients.brand.persona` (JSONB field)
- **JSON File**: `clients.json` → `clients[].brand.persona`

Additional metadata stored:
- `brand.persona_completed`: Boolean flag
- `brand.persona_completed_at`: ISO timestamp

## Integration with Content Generation

### Center Post Generation

When generating center posts, the system checks for `brand.persona`:

1. **If persona exists**: Uses the complete persona document as context
2. **If persona doesn't exist**: Falls back to legacy brand settings (mission, tone, values, etc.)

The persona document takes precedence and provides much richer context for content generation.

### Social Post Generation

Social posts also use the persona document when available, ensuring consistent voice across all platforms.

## Technical Details

### Interview Session Management

- Sessions are stored in-memory in `PersonaInterview.sessions`
- Each session maintains:
  - Conversation history with Claude
  - Answers collected
  - Current question number
  - Question tracking state

### Claude Integration

The interview uses Claude API to:
1. Ask questions based on the interview prompt
2. Push back on vague answers
3. Follow interesting threads
4. Generate the final persona document

### Conversation Flow

```
1. User starts interview → Claude receives initial prompt
2. Claude asks question 1 → Stored in conversation_history
3. User submits answer → Added to conversation_history
4. Claude asks question 2 → Based on previous answer
5. ... (repeat for 100 questions)
6. User completes → Claude generates persona document
7. User saves → Stored in brand.persona
```

## Best Practices

### For Users

1. **Be Honest**: Answer truthfully, not what you think sounds good
2. **Be Specific**: Give concrete examples, not vague preferences
3. **Focus on Rejections**: Think about what you'd NEVER do
4. **Use Voice Dictation**: Consider using tools like Wispr Flow for more natural answers
5. **Take Your Time**: This is your brand's DNA - invest the time

### For Developers

1. **Session Management**: Sessions are in-memory - consider persistence for production
2. **Error Handling**: Interview can fail if Claude API errors occur
3. **Token Limits**: Persona documents can be large - ensure Claude has sufficient max_tokens
4. **Fallback**: Always check for persona, but support legacy brand settings

## Future Enhancements

- [ ] Persist interview sessions to database
- [ ] Allow resuming interrupted interviews
- [ ] Add progress saving (auto-save answers)
- [ ] Support updating existing personas
- [ ] Add persona versioning
- [ ] Export persona as downloadable markdown file
- [ ] Import persona from existing markdown file
- [ ] A/B test content with/without persona

## Files

- **Frontend**: `web/templates/brand_persona_onboarding.html`
- **Backend Routes**: `app.py` (onboarding routes)
- **Interview Logic**: `content/persona_interview.py`
- **Content Integration**: `content/ai_client.py` (uses persona in prompts)
- **Derivative Generation**: `content/derivative_generator.py` (passes persona to social posts)

## Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Content System Implementation](./CONTENT_SYSTEM_IMPLEMENTATION.md)
- [Supabase Setup](./SUPABASE_SETUP.md)
