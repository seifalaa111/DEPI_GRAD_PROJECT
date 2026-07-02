# Lungify Project Documentation

## 1. Project Summary

Lungify is a research-oriented medical AI web project for lung CT screening. It combines:

- A `Next.js` frontend website and demo workspace
- A `FastAPI` backend for inference and report generation
- Exported model artifacts for binary screening and advanced follow-up analysis

The main product goal is to accept a **de-identified CT study as a DICOM ZIP**, run the AI pipeline, and return a structured **AI report** for review.

## 2. Core Product Scope

The primary workflow in Lungify is:

1. Upload a de-identified CT scan as a `.zip` containing a DICOM series
2. Run binary lung cancer screening
3. Build a readable AI report
4. Return the result to the frontend with recommendation text and disclaimer

This is the core experience that should be used when presenting the project to evaluators.

## 3. Important Note About Segmentation

**Segmentation in Lungify is a supplementary feature, not the core feature of the project.**

It should be described as:

- An **auxiliary visualization/localization feature**
- A **prototype enhancement** on top of the main screening/report workflow
- A **supporting output**, not the main decision output

What this means in practice:

- The main result is the **final assessment** and generated **report**
- Segmentation is only meant to add visual support when available
- The project should still be considered functional even if segmentation is unavailable in some runs
- Segmentation should not be presented as the main medical claim of the system

In the current backend behavior, segmentation is especially limited because:

- It is part of the advanced follow-up pipeline
- It is only attempted when the binary model predicts a malignant case
- It depends on the advanced model bundle being loaded successfully
- It is documented by the backend itself as a **prototype localization** capability

For engineering review, the safest wording is:

> Lungify's primary deliverable is CT-based screening and AI report generation. Segmentation is an additional prototype feature for visual support.

## 4. System Architecture

### Frontend

Location:

- `lungify-frontend/`

Main responsibilities:

- Public website pages
- Demo upload interface
- Proxy API routes
- Displaying the returned report, subtype suggestion, and segmentation images

Key frontend files:

- `lungify-frontend/app/page.tsx`
- `lungify-frontend/app/demo/page.tsx`
- `lungify-frontend/components/DemoClient.tsx`
- `lungify-frontend/app/api/predict/route.ts`

### Backend

Location:

- `lungify-backend/`

Main responsibilities:

- File validation
- ZIP extraction and DICOM preparation
- Model loading and inference
- Report construction
- Health and model metadata endpoints

Key backend files:

- `lungify-backend/app/main.py`
- `lungify-backend/app/api/routes.py`
- `lungify-backend/app/services/model_registry.py`
- `lungify-backend/app/services/pipeline_a_inference.py`
- `lungify-backend/app/services/pipeline_b_inference.py`

### Model Artifacts

Locations:

- `lungify-backend/weights/pipeline_a_model.pkl`
- `lungify-backend/weights/pipeline_b_models/`

## 5. Functional Flow

### Real Inference Flow

1. The user uploads a `.zip` file containing a de-identified DICOM series.
2. The frontend sends the file to its own `/api/predict` route.
3. If `LUNGIFY_BACKEND_URL` is configured, the frontend proxies the request to the FastAPI backend.
4. The backend validates the upload and safely extracts the ZIP.
5. `Pipeline A` performs the main binary screening step.
6. If the binary result is malignant and the advanced model is available, `Pipeline B` may add subtype support and segmentation output.
7. The backend builds a structured response and returns it to the frontend.
8. The frontend displays the report, probabilities, warnings, and images if available.

### Preview/Sample Flow

If the deployment is running without the real backend, or if the uploaded file is a single `.dcm`, `.png`, or `.jpg`, the frontend can still operate in built-in preview/sample mode.

This means:

- The interface still works
- The user can still see a report-style output
- But it is not full real DICOM ZIP inference

## 6. Accepted Inputs

### Real model input

- `.zip` containing a de-identified DICOM CT series

### Preview-only inputs

- `.dcm`
- `.png`
- `.jpg`
- `.jpeg`

Single-file uploads are preview mode only in the current product behavior.

## 7. Main Outputs

The backend response is centered around the following sections:

- `final_assessment`
- `subtype_suggestion`
- `segmentation`
- `report`
- `warnings`

### Final assessment

This is the most important output. It contains:

- Label
- Risk level
- Confidence
- Source

### Subtype suggestion

This is a supporting classification output and should not override the final screening assessment.

### Segmentation

This is the supplementary visualization section. It may include:

- Original image
- Mask image
- Overlay image
- Localization scope

Again, this should be treated as supplementary visual support, not as the main product result.

### Report

The report includes:

- Summary
- Recommendation
- Disclaimer

## 8. API Endpoints

Main backend endpoints:

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`
- `POST /predict/sample`

Practical meaning:

- `/health` checks backend and model readiness
- `/model-info` exposes model metadata and limitations
- `/predict` handles real upload inference
- `/predict/sample` returns a sample response for demos

## 9. Repository Structure

```text
DEPI-GRAD-PROJECT/
|- PROJECT_DOCUMENTATION.md
|- README.md
|- lungify-frontend/
|  |- app/
|  |- components/
|  |- src/lib/
|  `- public/assets/
`- lungify-backend/
   |- app/
   |- configs/
   |- tests/
   `- weights/
```

## 10. Local Development

### Backend

```bash
cd lungify-backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

### Frontend

```bash
cd lungify-frontend
npm install
npm run dev
```

Recommended local frontend environment:

```bash
LUNGIFY_BACKEND_URL=http://localhost:7860
```

## 11. Deployment Notes

### Frontend deployment

- Designed for `Vercel`
- Uses internal `/api/*` routes
- Can proxy to the real backend when `LUNGIFY_BACKEND_URL` is set

### Backend deployment

- Designed for `FastAPI`
- Can run in Docker-based environments such as Hugging Face Spaces or another Python hosting target

### Deployment behavior

- With backend configured: real ZIP inference is available
- Without backend configured: the site remains usable in preview/sample mode

## 12. Testing and Verification

Backend:

```bash
cd lungify-backend
python -m pytest -q
```

Frontend:

```bash
cd lungify-frontend
npm run build
```

## 13. Limitations and Safety Notes

- This is a research prototype, not a medical device
- It is not for clinical diagnosis
- Real inference expects de-identified DICOM ZIP input
- Segmentation is a prototype support feature and should not be treated as the core medical output
- Subtype output is supportive information and does not replace the main screening assessment

## 14. Recommended Evaluation Framing

When presenting this project to engineers or evaluators, describe it this way:

- Lungify is a CT screening and AI report generation platform
- The main deliverable is the screening result plus structured report
- The website, backend, and model integration are the core engineering scope
- Segmentation is an additional prototype feature for visual assistance

That framing matches the implemented behavior of the project and sets correct expectations.
