import { BadgeCheck, Brain, Code2, Presentation } from "lucide-react";

const roles = [
  { name: "AI Research", role: "Model training, evaluation, segmentation workflow", icon: Brain },
  { name: "Backend", role: "FastAPI inference, DICOM processing, deployment", icon: Code2 },
  { name: "Frontend", role: "Lungify website, demo interface, report viewer", icon: Presentation },
  { name: "Clinical Review", role: "Proposal alignment, safety language, presentation QA", icon: BadgeCheck }
];

export default function TeamPage() {
  return (
    <main className="page-frame">
      <section className="team-hero">
        <p className="eyebrow">Lungify Team</p>
        <h1>Built around one responsible AI workflow</h1>
      </section>
      <section className="team-grid">
        {roles.map((item) => {
          const Icon = item.icon;
          return (
            <article key={item.name}>
              <Icon size={24} />
              <h2>{item.name}</h2>
              <p>{item.role}</p>
            </article>
          );
        })}
      </section>
      <section className="disclaimer-band">
        <strong>Research prototype only.</strong>
        <span>Not for clinical diagnosis, radiology replacement, or autonomous medical decision-making.</span>
      </section>
    </main>
  );
}

