'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}

const WELCOME: Message = {
  id: 'welcome',
  role: 'assistant',
  text: 'Olá! Sou o assistente virtual do IESB. Posso te ajudar com dúvidas sobre Extensão Curricularizada e Atividades Complementares. Como posso ajudar?',
};

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId] = useState<string>(() => uid());
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setMessages(prev => [...prev, { id: uid(), role: 'user', text }]);
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, message: text, userId }),
      });
      const data = await res.json() as { sessionId?: string; text?: string; error?: string };

      if (!res.ok || data.error) throw new Error(data.error ?? 'Erro desconhecido');

      if (data.sessionId) setSessionId(data.sessionId);
      setMessages(prev => [...prev, { id: uid(), role: 'assistant', text: data.text ?? '' }]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { id: uid(), role: 'assistant', text: `Ocorreu um erro: ${(err as Error).message}` },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, loading, sessionId, userId]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div id="chat-layout">
      {/* Header */}
      <header id="chat-header">
        <div className="d-flex align-items-center gap-3">
          <div
            style={{
              width: 44, height: 44, borderRadius: '50%',
              background: 'rgba(255,255,255,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.4rem',
            }}
          >
            🎓
          </div>
          <div>
            <div className="fw-bold fs-5 lh-1">Assistente IESB</div>
            <div style={{ fontSize: '0.8rem', opacity: 0.75, marginTop: 2 }}>
              Extensão Curricularizada &amp; Atividades Complementares
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <main id="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`msg-row ${msg.role === 'user' ? 'user' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="avatar bot">🎓</div>
            )}
            <div className={`bubble ${msg.role === 'user' ? 'user' : 'bot'}`}>
              {msg.text}
            </div>
            {msg.role === 'user' && (
              <div className="avatar user">👤</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="msg-row">
            <div className="avatar bot">🎓</div>
            <div className="bubble bot" style={{ padding: '0.75rem 1rem' }}>
              <div className="typing-dots">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* Input */}
      <footer id="chat-footer">
        <div className="d-flex align-items-end gap-2">
          <textarea
            ref={textareaRef}
            id="chat-input"
            rows={1}
            placeholder="Escreva sua dúvida... (Enter para enviar)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={loading}
          />
          <button id="send-btn" onClick={send} disabled={loading || !input.trim()} aria-label="Enviar">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
              <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/>
            </svg>
          </button>
        </div>
        <div className="text-muted text-center mt-2" style={{ fontSize: '0.72rem' }}>
          As respostas são baseadas nos guias oficiais do IESB. Para dúvidas não cobertas, entre em contato com{' '}
          <a href="mailto:ativ.complementar@iesb.br" className="text-muted">ativ.complementar@iesb.br</a>.
        </div>
      </footer>
    </div>
  );
}
