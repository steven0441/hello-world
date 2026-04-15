import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import { checkMilestones } from '@/lib/finance';

export async function GET() {
  try {
    checkMilestones();
    const db = getDb();
    const milestones = db.prepare(
      'SELECT id, agent_id, key_name as key, label, icon, achieved_at FROM milestones ORDER BY agent_id, id ASC'
    ).all();
    return NextResponse.json({ milestones });
  } catch (err) {
    console.error('[milestones]', err);
    return NextResponse.json({ error: 'Failed to load milestones' }, { status: 500 });
  }
}
