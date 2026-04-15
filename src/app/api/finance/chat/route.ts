import { NextRequest } from 'next/server';
import { AGENT_CONFIG, FINANCE_SYSTEM_PROMPT } from '@/config/agents';
import { streamAgentResponse } from '@/lib/agent-client';
import { getFinanceSummary, getBills, getDebts, getConversationHistory, saveMessage, logActivity } from '@/lib/finance';

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();
    if (!message) {
      return new Response('Missing message', { status: 400 });
    }

    // Build context snapshot for Bean
    const summary = getFinanceSummary();
    const bills = getBills();
    const debts = getDebts();
    const history = getConversationHistory('finance', 10);

    const contextBlock = `
CURRENT FINANCIAL DATA:
- Monthly Income: $${summary.monthlyIncome.toFixed(2)}
- Savings: $${summary.savings.toFixed(2)}
- Total Debt: $${summary.totalDebt.toFixed(2)}
- Net Worth: $${summary.netWorth.toFixed(2)}
- Budget Health: ${summary.budgetHealth}%
- Bills due in next 14 days: ${summary.upcomingBills.map(b => `${b.name} ($${b.amount}) in ${b.daysUntilDue} days`).join(', ') || 'None'}
- All active bills: ${bills.map(b => `${b.name} $${b.amount}/mo (due day ${b.dueDay})`).join(', ')}
- Debts: ${debts.map(d => `${d.name}: $${d.balance} @ ${d.interestRate}% (min $${d.minimumPayment}/mo)`).join(', ') || 'None'}
`;

    const systemWithContext = FINANCE_SYSTEM_PROMPT + '\n\n' + contextBlock;

    // Save user message
    saveMessage('finance', 'user', message);

    const messages = [
      ...history.map(h => ({ role: h.role as 'user' | 'assistant', content: h.content })),
      { role: 'user' as const, content: message },
    ];

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        let fullResponse = '';

        await streamAgentResponse(
          AGENT_CONFIG.finance,
          systemWithContext,
          messages,
          (chunk) => {
            fullResponse += chunk;
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: chunk })}\n\n`));
          },
          () => {
            saveMessage('finance', 'assistant', fullResponse);
            logActivity('finance', 'info', `Bean responded: "${fullResponse.slice(0, 80)}..."`);
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
    console.error('[finance/chat]', err);
    return new Response('Internal server error', { status: 500 });
  }
}
