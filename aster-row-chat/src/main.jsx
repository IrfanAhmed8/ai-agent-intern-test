import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000/chat";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event?.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((current) => [...current, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const data = await response.json();

      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.answer ?? "No answer was returned." }
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Spikes in demand are usually temporary. Please try again later."
        }
      ]);
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="chat-shell">
        <header className="header">
          <div>
            <div className="eyebrow">ASTER & ROW</div>
            <h1>How can we help?</h1>
          </div>
          <span className="status-dot" title="Assistant ready" />
        </header>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Ask us anything about Aster & Row.</p>
              <span>Product care, orders, materials, and more.</span>
            </div>
          ) : (
            messages.map((message, index) => (
              <article
                key={index}
                className={`message ${message.role === "user" ? "user" : "assistant"}`}
              >
                <div className="bubble">
                  {message.content.split("\n").map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < message.content.split("\n").length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
              </article>
            ))
          )}

          {loading && (
            <article className="message assistant">
              <div className="bubble typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}
        </div>

        <form className="composer" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Write a message..."
            aria-label="Message"
            disabled={loading}
          />
          <button type="submit" disabled={!input.trim() || loading}>
            Send
          </button>
        </form>

        <footer>ASTER & ROW · CUSTOMER ASSISTANCE</footer>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
