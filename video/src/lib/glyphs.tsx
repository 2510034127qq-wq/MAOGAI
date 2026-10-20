import React from "react";
import { C } from "./theme";

/** small woodcut-like factory: sawtooth roof + chimney */
export const Factory: React.FC<{ w?: number; color?: string; clip?: number }> = ({ w = 120, color = C.ink, clip = 1 }) => (
  <svg width={w} height={w * 0.8} viewBox="0 0 120 96" style={{ overflow: "visible" }}>
    <defs>
      <clipPath id={`fc${Math.round(clip * 100)}`}>
        <rect x={0} y={-40} width={120 * clip} height={140} />
      </clipPath>
    </defs>
    <g clipPath={`url(#fc${Math.round(clip * 100)})`}>
      <rect x={88} y={6} width={12} height={50} fill={color} />
      <path d="M4,92 L4,48 L28,32 L28,48 L52,32 L52,48 L76,32 L76,48 L100,32 L100,48 L116,48 L116,92 Z" fill={color} />
      {[0, 1, 2, 3].map((i) => (
        <rect key={i} x={14 + i * 25} y={62} width={11} height={14} fill={C.paper} />
      ))}
    </g>
    {clip < 1 && <line x1={120 * clip} y1={20} x2={120 * clip} y2={96} stroke={C.red} strokeWidth={2} strokeDasharray="4 4" />}
  </svg>
);

export const Gear: React.FC<{ w?: number; color?: string; rot?: number }> = ({ w = 90, color = C.ink, rot = 0 }) => {
  const teeth = 10;
  const pts: string[] = [];
  for (let i = 0; i < teeth * 2; i++) {
    const a = (i / (teeth * 2)) * Math.PI * 2;
    const r = i % 2 ? 36 : 44;
    const a1 = a - 0.11;
    const a2 = a + 0.11;
    pts.push(`${50 + Math.cos(a1) * r},${50 + Math.sin(a1) * r}`, `${50 + Math.cos(a2) * r},${50 + Math.sin(a2) * r}`);
  }
  return (
    <svg width={w} height={w} viewBox="0 0 100 100" style={{ rotate: `${rot}deg` }}>
      <polygon points={pts.join(" ")} fill={color} />
      <circle cx={50} cy={50} r={13} fill={C.paper} />
    </svg>
  );
};
