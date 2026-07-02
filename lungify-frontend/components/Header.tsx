import Link from "next/link";
import { Activity, BrainCircuit, FlaskConical, Users } from "lucide-react";

const links = [
  { href: "/demo", label: "Demo", icon: Activity },
  { href: "/model", label: "Model", icon: BrainCircuit },
  { href: "/team", label: "Team", icon: Users }
];

export function Header() {
  return (
    <header className="site-header">
      <Link href="/" className="brand" aria-label="Lungify home">
        <FlaskConical size={20} />
        <span>Lungify</span>
      </Link>
      <nav aria-label="Main navigation">
        {links.map((item) => {
          const Icon = item.icon;
          return (
            <Link href={item.href} key={item.href}>
              <Icon size={16} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

