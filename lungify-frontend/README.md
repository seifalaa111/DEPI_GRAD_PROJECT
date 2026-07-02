# Lungify Frontend

Next.js app for the Lungify website and AI report demo.

## Routes

- `/`: scroll-story homepage.
- `/demo`: upload/report interface.
- `/model`: model explanation and exported evaluation visuals.
- `/team`: project roles and disclaimer.

## Environment

```bash
LUNGIFY_BACKEND_URL=http://localhost:7860
```

The frontend now talks to its own `/api/*` routes first.

- If `LUNGIFY_BACKEND_URL` is set, those routes proxy to the real FastAPI backend.
- If it is not set, the Vercel deployment stays usable in built-in sample/preview mode.
- If `LUNGIFY_BACKEND_URL` is set but the backend is down, real upload requests return an explicit error instead of silently falling back to preview mode.

On Vercel, set `LUNGIFY_BACKEND_URL` to the FastAPI or Hugging Face Space URL if you want real ZIP inference.

## Commands

```bash
npm install
npm run dev
npm run build
```
