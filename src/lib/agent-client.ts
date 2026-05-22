import type { AgentConfig, AgentMessage } from '@/types';

/**
 * AgentClient — unified adapter for Anthropic, Ollama, and OpenAI backends.
 * Swap the config in src/config/agents.ts to change which backend/model an agent uses.
 */
export async function streamAgentResponse(
  config: AgentConfig,
  systemPrompt: string,
  messages: AgentMessage[],
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void
): Promise<void> {
  try {
    switch (config.backend) {
      case 'anthropic':
        await streamAnthropic(config, systemPrompt, messages, onChunk, onDone);
        break;
      case 'ollama':
        await streamOllama(config, systemPrompt, messages, onChunk, onDone);
        break;
      case 'openai':
        await streamOpenAI(config, systemPrompt, messages, onChunk, onDone);
        break;
      default:
        throw new Error(`Unknown backend: ${config.backend}`);
    }
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
  }
}

async function streamAnthropic(
  config: AgentConfig,
  systemPrompt: string,
  messages: AgentMessage[],
  onChunk: (text: string) => void,
  onDone: () => void
) {
  const { default: Anthropic } = await import('@anthropic-ai/sdk');
  const client = new Anthropic({ apiKey: config.apiKey });

  const stream = await client.messages.stream({
    model: config.model,
    max_tokens: 1024,
    system: systemPrompt,
    messages: messages.map(m => ({ role: m.role, content: m.content })),
  });

  for await (const chunk of stream) {
    if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
      onChunk(chunk.delta.text);
    }
  }
  onDone();
}

async function streamOllama(
  config: AgentConfig,
  systemPrompt: string,
  messages: AgentMessage[],
  onChunk: (text: string) => void,
  onDone: () => void
) {
  const baseUrl = config.baseUrl || 'http://localhost:11434';
  const ollamaMessages = [
    { role: 'system', content: systemPrompt },
    ...messages.map(m => ({ role: m.role, content: m.content })),
  ];

  const response = await fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: config.model, messages: ollamaMessages, stream: true }),
  });

  if (!response.ok) {
    throw new Error(`Ollama error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body from Ollama');

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const lines = decoder.decode(value).split('\n').filter(Boolean);
    for (const line of lines) {
      try {
        const parsed = JSON.parse(line);
        if (parsed.message?.content) {
          onChunk(parsed.message.content);
        }
      } catch {
        // skip malformed lines
      }
    }
  }
  onDone();
}

async function streamOpenAI(
  config: AgentConfig,
  systemPrompt: string,
  messages: AgentMessage[],
  onChunk: (text: string) => void,
  onDone: () => void
) {
  const baseUrl = config.baseUrl || 'https://api.openai.com/v1';
  const openaiMessages = [
    { role: 'system', content: systemPrompt },
    ...messages.map(m => ({ role: m.role, content: m.content })),
  ];

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({ model: config.model, messages: openaiMessages, stream: true }),
  });

  if (!response.ok) {
    throw new Error(`OpenAI error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body from OpenAI');

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const lines = decoder.decode(value).split('\n');
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const data = line.slice(6).trim();
      if (data === '[DONE]') continue;
      try {
        const parsed = JSON.parse(data);
        const text = parsed.choices?.[0]?.delta?.content;
        if (text) onChunk(text);
      } catch {
        // skip
      }
    }
  }
  onDone();
}
