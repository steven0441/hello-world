import { NextRequest, NextResponse } from 'next/server';
import { getBills, addBill, deleteBill } from '@/lib/finance';

export async function GET() {
  try {
    const bills = getBills();
    return NextResponse.json({ bills });
  } catch (err) {
    console.error('[finance/bills GET]', err);
    return NextResponse.json({ error: 'Failed to load bills' }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, amount, dueDay, category } = body;

    if (!name || !amount || !dueDay || !category) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const bill = addBill(name, Number(amount), Number(dueDay), category);
    return NextResponse.json(bill, { status: 201 });
  } catch (err) {
    console.error('[finance/bills POST]', err);
    return NextResponse.json({ error: 'Failed to create bill' }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const id = Number(searchParams.get('id'));
    if (!id) return NextResponse.json({ error: 'Missing id' }, { status: 400 });

    const success = deleteBill(id);
    if (!success) return NextResponse.json({ error: 'Bill not found' }, { status: 404 });

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('[finance/bills DELETE]', err);
    return NextResponse.json({ error: 'Failed to delete bill' }, { status: 500 });
  }
}
