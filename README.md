# Radiomics & Deep Learning for Early Lung Cancer Diagnosis

A DEPI (Digital Egypt Pioneers Initiative) graduation project that applies Radiomics feature extraction and 3D deep learning on the LIDC-IDRI CT scan dataset to detect and classify lung cancer at an early stage.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Pipelines](#pipelines)
  - [1. Radiomics Feature Extraction](#1-radiomics-feature-extraction)
  - [2. Multimodal Binary Classifier (PyTorch)](#2-multimodal-binary-classifier-pytorch)
  - [3. Research-Grade 3-Class Classifier (PyTorch)](#3-research-grade-3-class-classifier-pytorch)
  - [4. TensorFlow / Keras Multimodal Classifier](#4-tensorflow--keras-multimodal-classifier)
- [Model Architectures](#model-architectures)
- [Technology Stack](#technology-stack)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)

---

## Project Overview

Lung cancer is one of the leading causes of cancer-related mortality worldwide. Early detection dramatically improves patient outcomes. This project explores two complementary approaches:

1. **Radiomics** — extracting hundreds of hand-crafted quantitative features (intensity, shape, texture, filter-based) from 3D CT scans and tumor masks, followed by statistical feature selection.
2. **Deep Learning** — training 3D Convolutional Neural Networks directly on CT volumes to classify nodules as benign, primary lung cancer, or metastatic.

Both approaches use the publicly available **LIDC-IDRI** dataset and are implemented across three Jupyter notebooks covering the full pipeline from raw DICOM/NIfTI data to trained models.

---

## Dataset

**LIDC-IDRI** (Lung Image Database Consortium and Image Database Resource Initiative)

| Property | Details |
|---|---|
| Source | The Cancer Imaging Archive (TCIA) |
| Modality | CT scans (DICOM) |
| Size | ~133 GB, ~1,000 patients |
| Labels | Patient-level diagnosis (Unknown, Benign, Malignant-Primary, Malignant-Metastatic) |
| Nodule annotation | Malignancy score 1–5 per nodule |

The dataset is **not included** in this repository due to its size. Download it from [TCIA](https://www.cancerimagingarchive.net/collection/lidc-idri/).

Two data formats are used:
- **DICOM** — raw CT scans organized per patient folder (used by the PyTorch pipelines)
- **NIfTI** (`.nii.gz`) — preprocessed CT volumes + binary tumor masks (used by the Keras pipeline and Radiomics extraction)

---

## Project Structure

```
Medical_Project/
├── FeatureExtraction.ipynb         # Radiomics extraction + feature selection
├── notebook 1.ipynb                # PyTorch deep learning pipelines (binary + 3-class)
├── Ai_Models_Medical (1).ipynb     # TensorFlow/Keras multimodal pipeline
├── Radiomics-For-Early-Cancer-Diagnosis.pdf  # Research reference paper
├── Medical Paper.docx              # Project paper
└── Medical_Project_Report.docx     # Full project report
```

---

## Pipelines

### 1. Radiomics Feature Extraction

**Notebook:** `FeatureExtraction.ipynb`

Extracts quantitative imaging biomarkers from preprocessed NIfTI CT volumes and their corresponding binary tumor masks using **PyRadiomics**.

#### Feature Categories

| Category | Features |
|---|---|
| **First-Order** | Mean, Median, Entropy, Energy, Skewness, Kurtosis — captures intensity distribution and tumor brightness |
| **Shape** | Volume, Surface Area, Sphericity, Compactness, Elongation — irregular shapes indicate aggressive tumors |
| **GLCM** | Gray-Level Co-occurrence Matrix — spatial pixel relationships |
| **GLRLM** | Gray-Level Run Length Matrix — continuous intensity run patterns |
| **GLSZM** | Gray-Level Size Zone Matrix — homogeneous region sizes |
| **GLDM** | Gray-Level Dependence Matrix — voxel dependence patterns |
| **NGTDM** | Neighboring Gray Tone Difference Matrix — local contrast and coarseness |
| **Wavelet** | Multi-scale frequency decomposition |
| **LoG** | Laplacian of Gaussian (σ = 1.0, 2.0, 3.0) — edge and blob detection |
| **Gradient** | Intensity transition features |
| **Square / SquareRoot / Log / Exp** | Non-linear filter-based features |

#### Feature Selection Pipeline

```
Raw features  →  Variance Threshold  →  LASSO (LassoCV, 5-fold)  →  PCA (95% variance)
```

- **Variance Threshold**: removes near-zero variance (uninformative) features
- **LASSO**: L1 regularization to select the most predictive features
- **PCA**: reduces dimensionality while retaining 95% of explained variance

Outputs: `radiomics_features.csv`, `features_lasso_selected.csv`, `features_pca_reduced.csv`

---

### 2. Multimodal Binary Classifier (PyTorch)

**Notebook:** `notebook 1.ipynb` — Cell "ALL-IN-ONE TRAINING"

Classifies each patient's lung nodule as **benign (0)** or **malignant (1)** using a dual-input model that fuses 3D CT image features with clinical tabular data.

| Config | Value |
|---|---|
| Framework | PyTorch |
| Input | DICOM CT scans + tabular clinical features |
| Task | Binary classification (benign vs. malignant) |
| Target shape | 96 × 160 × 160 voxels |
| Batch size | 2 |
| Epochs | 15 |
| Learning rate | 1e-4 |
| Optimizer | Adam |
| Mixed precision | Yes (AMP) |
| Split | 80/20 train/val |

**Architecture:**
- **Image Branch:** 3D ResNet with Squeeze-Excitation (SE) blocks — Stem → 3 residual stages (16→32→64→128 channels) → AdaptiveAvgPool3D → Dense(256)
- **Tabular Branch:** Linear layers for clinical feature encoding
- **Fusion:** Concatenation → classification head with dropout → sigmoid output

---

### 3. Research-Grade 3-Class Classifier (PyTorch)

**Notebook:** `notebook 1.ipynb` — Cell "Research-Grade Pipeline"

A more rigorous pipeline that classifies patients into **3 diagnostic classes** using image data only. Tabular features from the TCIA Excel file were excluded after a leakage analysis revealed they are all derived from the diagnosis label itself.

| Class | Label |
|---|---|
| 0 | Benign / Unknown |
| 1 | Malignant — Primary Lung Cancer |
| 2 | Malignant — Metastatic |

| Config | Value |
|---|---|
| Framework | PyTorch |
| Input | DICOM CT scans (image-only) |
| Input channels | 2 (standard HU window + lung window) |
| Target shape | 64 × 128 × 128 voxels |
| Batch size | 2 |
| Epochs | 40 |
| Learning rate | 3e-4 with cosine annealing |
| Loss | Focal Loss (γ = 2.0) + class weighting |
| Cross-validation | 5-Fold Stratified K-Fold |
| Early stopping | Patience = 8 |
| Mixed precision | Yes (AMP) |

**Architecture:** 3D ResNet-SE backbone with **CBAM** (Convolutional Block Attention Module) attention  
- Channels: 16 → 32 → 64 → 128 → 256  
- Dual-channel input encodes two CT windowing levels simultaneously

**Data Augmentation:**

| Augmentation | Probability | Details |
|---|---|---|
| Horizontal flip | 50% | |
| Rotation | 50% | ±15° |
| Gaussian noise | 30% | std = 0.02 |
| Gamma correction | 30% | γ ∈ [0.75, 1.25] |
| Elastic deformation | 20% | α=10, σ=2 |

**Evaluation:** Accuracy, macro/weighted F1, ROC-AUC (One-vs-Rest), per-class precision/recall, confusion matrix, calibration curves, per-class threshold tuning.

---

### 4. TensorFlow / Keras Multimodal Classifier

**Notebook:** `Ai_Models_Medical (1).ipynb`

Classifies nodule **malignancy score** (1–5 scale) using a dual-input Keras model that simultaneously processes a 2-channel 3D volume (CT + tumor mask stacked) and tabular radiomics features.

| Config | Value |
|---|---|
| Framework | TensorFlow / Keras |
| Input (image) | NIfTI volumes: preprocessed_volume.nii.gz + tumor_mask.nii.gz |
| Input (tabular) | Scaled radiomics/clinical features |
| Target | Malignancy score (5-class: 0–4) |
| Volume size | 32 × 64 × 64 × 2 (Depth × H × W × Channels) |
| Batch size | 8 |
| Epochs | 20 |
| Learning rate | 1e-4 |
| Optimizer | Adam |
| Loss | Sparse Categorical Crossentropy |
| Early stopping | Patience = 5 |
| Split | GroupShuffleSplit (patient-level, no leakage) |

**Architecture:**

```
Image Branch (3D CNN):
  Conv3D(32) → MaxPool3D → BatchNorm
  Conv3D(64) → MaxPool3D → BatchNorm
  GlobalAveragePooling3D → Dense(64)

Tabular Branch:
  Dense(64) → Dropout(0.2) → Dense(32)

Fusion:
  Concatenate → Dense(64) → Dropout(0.3) → Dense(num_classes, softmax)
```

**Custom Data Generator:** `MultimodalDataGenerator` loads NIfTI volumes on-the-fly, resizes them to the target shape (nearest-neighbor for masks, spline for CT), normalizes CT voxel values to [0, 1], and stacks volume + mask into a 2-channel array.

---

## Model Architectures

### SE Block (Squeeze-Excitation)
Recalibrates channel-wise feature responses by modelling inter-channel dependencies: global average pooling → FC → ReLU → FC → Sigmoid → channel-wise scaling.

### CBAM (Convolutional Block Attention Module)
Applied in the research-grade pipeline — applies both **channel attention** (what to focus on) and **spatial attention** (where to focus) sequentially.

### 3D Residual Block
Each block: Conv3D → BN → ReLU → Conv3D → BN → SE Block → skip connection (with 1×1 Conv if dimensions change).

---

## Technology Stack

| Category | Libraries |
|---|---|
| Deep Learning | PyTorch, TensorFlow/Keras |
| Medical Imaging | nibabel, pydicom, SimpleITK |
| Radiomics | PyRadiomics |
| Image Processing | SciPy (ndimage), scikit-image |
| ML / Statistics | scikit-learn |
| Data | NumPy, Pandas, openpyxl |
| Visualization | Matplotlib, Seaborn |
| GPU | CUDA (via PyTorch AMP) |

---

## Setup & Installation

```bash
# PyTorch pipelines (notebook 1.ipynb)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install pandas openpyxl xlrd pydicom scipy scikit-learn numpy matplotlib seaborn

# TensorFlow/Keras pipeline (Ai_Models_Medical)
pip install tensorflow nibabel scipy scikit-learn pandas numpy

# Radiomics extraction (FeatureExtraction.ipynb)
pip install pyradiomics SimpleITK pydicom scikit-image pandas matplotlib scikit-learn
```

---

## How to Run

### Radiomics Feature Extraction
1. Upload preprocessed NIfTI data to Google Drive under `Medical Project/PREPROCESSED DATA/`
2. Each patient folder must contain:
   - `preprocessed_volume.nii.gz` — normalized CT volume
   - `tumor_mask.nii.gz` — binary tumor mask
3. Open `FeatureExtraction.ipynb` in Google Colab and run all cells
4. Feature CSVs are saved to `Medical Project/` in Google Drive

### PyTorch Pipelines (notebook 1.ipynb)
1. Download LIDC-IDRI dataset from TCIA
2. Update `EXCEL_PATH` and `DICOM_ROOT` in the Config section
3. Ensure CUDA-compatible GPU is available (recommended)
4. Run the training cell; model checkpoints are saved as `.pt` files
5. Run the test/inference cell to evaluate on held-out patients

### Keras Pipeline (Ai_Models_Medical.ipynb)
1. Prepare the central Excel/CSV file with patient metadata and malignancy scores
2. Set `EXCEL_FILE_PATH` and `IMAGE_ROOT_DIR` in the `__main__` block
3. Run all cells; the pipeline handles loading, preprocessing, model building, and training automatically

---

## Research Reference

This project is grounded in the paper included in this repository:

> **Radiomics for Early Cancer Diagnosis** — `Radiomics-For-Early-Cancer-Diagnosis.pdf`

---

*DEPI Graduation Project — Digital Egypt Pioneers Initiative*
