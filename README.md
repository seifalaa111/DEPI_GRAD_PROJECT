# Lungify

Lungify is split into two deployable apps:

- `lungify-backend`: FastAPI AI service for CT volume inference, report building, and Hugging Face Docker Spaces deployment.
- `lungify-frontend`: Next.js website and demo interface for Vercel deployment.

## Local Run

Backend:

```bash
cd lungify-backend
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

Frontend:

```bash
cd lungify-frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:7860` for local frontend-to-backend calls.

## Verification

```bash
cd lungify-backend
python -m pytest -q

cd ../lungify-frontend
npm run build
```

Real inference requires a de-identified DICOM CT series ZIP. Single `.dcm`, `.png`, and `.jpg` uploads are preview mode only.

