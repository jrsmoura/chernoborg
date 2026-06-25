import { NextRequest, NextResponse } from 'next/server';

const ADK_BASE = process.env.ADK_BASE_URL ?? 'http://localhost:8000';
const APP_NAME = 'assistente_iesb';

interface AdkEvent {
  author?: string;
  content?: { parts?: Array<{ text?: string; functionCall?: unknown }> };
}

function extractText(events: AdkEvent[]): string {
  for (let i = events.length - 1; i >= 0; i--) {
    const ev = events[i];
    if (ev.author === APP_NAME && ev.content?.parts) {
      const part = ev.content.parts.find(p => p.text && !p.functionCall);
      if (part?.text) return part.text;
    }
  }
  return 'Não foi possível obter uma resposta. Tente novamente.';
}

export async function POST(req: NextRequest) {
  const { sessionId: existingSession, message, userId } = await req.json() as {
    sessionId?: string;
    message: string;
    userId: string;
  };

  let sessionId = existingSession;

  if (!sessionId) {
    const res = await fetch(
      `${ADK_BASE}/apps/${APP_NAME}/users/${userId}/sessions`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }
    );
    if (!res.ok) {
      return NextResponse.json({ error: 'Erro ao criar sessão.' }, { status: 502 });
    }
    const session = await res.json() as { id: string };
    sessionId = session.id;
  }

  const runRes = await fetch(`${ADK_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      app_name: APP_NAME,
      user_id: userId,
      session_id: sessionId,
      new_message: { role: 'user', parts: [{ text: message }] },
    }),
  });

  if (!runRes.ok) {
    return NextResponse.json({ error: 'Erro ao contatar o assistente.' }, { status: 502 });
  }

  const events = await runRes.json() as AdkEvent[];
  return NextResponse.json({ sessionId, text: extractText(events) });
}
