import Image from "next/image";
import { Activity, BarChart3, BrainCircuit, ScanLine } from "lucide-react";
import type { ReactNode } from "react";

const figures = [
  { src: "/assets/training_curves_binary.png", title: "Pipeline A Training Curves" },
  { src: "/assets/cm_binary.png", title: "Binary Confusion Matrix" },
  { src: "/assets/final_test_metrics_bar.png", title: "Pipeline B Final Metrics" },
  { src: "/assets/segmentation_distribution.png", title: "Segmentation Distribution" },
  { src: "/assets/seg_vis_LIDC-IDRI-0939.png", title: "Primary Lung Cancer Localization" },
  { src: "/assets/seg_vis_LIDC-IDRI-0285.png", title: "Metastatic Case Visualization" }
];

export default function ModelPage() {
  return (
    <main className="page-frame">
      <section className="model-hero">
        <p className="eyebrow">Technical Model</p>
        <h1>CT classification and tumor localization</h1>
        <div className="model-cards">
          <ModelCard icon={<BrainCircuit />} label="Binary Engine" value="3D ResNet-SE + tabular MLP" />
          <ModelCard icon={<Activity />} label="Subtype Engine" value="5-fold 3-class ensemble" />
          <ModelCard icon={<ScanLine />} label="Segmentation" value="3D U-Net center-patch localization" />
          <ModelCard icon={<BarChart3 />} label="Backend Mode" value="FastAPI on Docker Space" />
        </div>
      </section>
      <section className="figure-grid">
        {figures.map((figure) => (
          <article className="figure-card" key={figure.src}>
            <Image src={figure.src} alt={figure.title} width={1200} height={700} />
            <h2>{figure.title}</h2>
          </article>
        ))}
      </section>
    </main>
  );
}

function ModelCard({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <article>
      <div className="icon-badge">{icon}</div>
      <small>{label}</small>
      <strong>{value}</strong>
    </article>
  );
}
