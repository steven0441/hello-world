import { NextRequest } from 'next/server';
import { AGENT_CONFIG, ORCHESTRATOR_SYSTEM_PROMPT } from '@/config/agents';
import { streamAgentResponse } from '@/lib/agent-client';
import { getFinanceSummary, logActivity, getConversationHistory, saveMessage } from '@/lib/finance';

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();
    if (!message) {
      return new Response('Missing message', { status: 400 });
    }

    const summary = getFinanceSummary();
    const contextBlock = `
DUNGEON STATUS REPORT:
- Finance Slave (Bean Counter): ACTIVE
- Net Worth: $${summary.netWorth.toFixed(2)}
- Monthly Income: $${summary.monthlyIncome.toFixed(2)}
- Budget Health: ${summary.budgetHealth}%
- Upcoming bills: ${summary.upcomingBills.length} in the next 14 days
- Urgent (due in ≤3 days): ${summary.upcomingBills.filter(b => b.daysUntilDue <= 3).map(b => b.name).join(', ') || 'None'}
`;

    const history = getConversationHistory('orchestrator', 6);
    saveMessage('orchestrator', 'user', message);

    const messages = [
      ...history.map(h => ({ role: h.role as 'user' | 'assistant', content: h.content })),
      { role: 'user' as const, content: message },
    ];

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        let fullResponse = '';

        await streamAgentResponse(
          AGENT_CONFIG.orchestrator,
          ORCHESTRATOR_SYSTEM_PROMPT + '\n\n' + contextBlock,
          messages,
          (chunk) => {
            fullResponse += chunk;
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: chunk })}\n\n`));
          },
          () => {
            saveMessage('orchestrator', 'assistant', fullResponse);
            logActivity('orchestrator', 'info', `Orchestrator: "${fullResponse.slice(0, 80)}..."`);
            controller.enqueue(encoder.encode('data: [DONE]\n\n'));
            controller.close();
          },
          (err) => {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: err.message })}\n\n`));
            controller.close();
          }
        );
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  } catch (err) {
    console.error('[orchestrator/command]', err);
    return new Response('Internal server error', { status: 500 });
  }
}
