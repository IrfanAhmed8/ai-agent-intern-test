# Aster & Row Chat

Simple React chat UI for the Aster & Row API.

## Run

```bash
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

## API contract

The frontend sends:

```http
POST http://127.0.0.1:8000/chat
Content-Type: application/json

{"message":"Your question"}
```

It expects JSON containing:

```json
{
  "answer": "The assistant response..."
}
```

If the API is served from a different origin, enable CORS on the backend for the frontend's origin (for example `http://localhost:5173`).
