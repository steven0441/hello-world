import { NextResponse } from 'next/server';
import { getFinanceSummary } from '@/lib/finance';

export async function GET() {
  try {
    const summary = getFinanceSummary();
    return NextResponse.json(summary);
  } catch (err) {
    console.error('[finance/summary]', err);
    return NextResponse.json({ error: 'Failed to load summary' }, { status: 500 });
  }
}
