import Link from "next/link";
import { ArrowRight, BrainCircuit, FileArchive, Microscope, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { LungVisual } from "@/components/LungVisual";

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <div className="hero-media" />
        <div className="hero-content">
          <p className="eyebrow">Breathing Wellness</p>
          <h1>Lungify</h1>
          <p>AI-powered lung cancer detection and tumor segmentation from thoracic CT scans.</p>
          <Link className="hero-action" href="/demo">
            <span>Open demo</span>
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      <section className="scroll-story">
        <div className="sticky-visual">
          <LungVisual />
        </div>
        <div className="story-copy">
          <StoryStep icon={<FileArchive />} title="Upload CT Series" text="DICOM ZIP input becomes a normalized 3D volume." />
          <StoryStep icon={<BrainCircuit />} title="Screen Cancer Risk" text="FusionModel combines CT volume features with clinical metadata defaults." />
          <StoryStep icon={<Microscope />} title="Suggest Subtype" text="The multiclass engine estimates benign, primary lung cancer, or metastatic patterns." />
          <StoryStep icon={<ShieldCheck />} title="Build One Report" text="The result is a single Lungify AI Report with a clear disclaimer." />
        </div>
      </section>

      <section className="dashboard-band">
        <div>
          <p className="eyebrow">System Output</p>
          <h2>One clean medical AI report</h2>
        </div>
        <div className="report-preview">
          <span>Final Assessment</span>
          <strong>Malignant</strong>
          <span>Cancer Risk</span>
          <strong>High</strong>
          <span>Subtype Suggestion</span>
          <strong>Primary Lung Cancer</strong>
        </div>
      </section>
    </main>
  );
}

function StoryStep({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return (
    <article className="story-step">
      <div className="icon-badge">{icon}</div>
      <h2>{title}</h2>
      <p>{text}</p>
    </article>
  );
}
