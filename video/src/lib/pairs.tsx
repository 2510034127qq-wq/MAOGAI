import React from "react";
import { C, F } from "./theme";

export const NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"];
export const PAIRS: [string, string][] = [
  ["重工业", "轻工业、农业"],
  ["沿海工业", "内地工业"],
  ["经济建设", "国防建设"],
  ["国家", "生产单位、个人"],
  ["中央", "地方"],
  ["汉族", "少数民族"],
  ["党", "非党"],
  ["革命", "反革命"],
  ["是", "非"],
  ["中国", "外国"],
];
export const GROUPS = [
  { no: "壹", title: "经济结构与空间布局", idx: [0, 1, 2] },
  { no: "贰", title: "利益分配与治理体系", idx: [3, 4] },
  { no: "叁", title: "社会生态与政治关系", idx: [5, 6, 7, 8] },
  { no: "肆", title: "独立自主与对外开放", idx: [9] },
];

/** one relation drawn as two ends joined by a line; `tilt` in degrees, `k` draws the line 0..1 */
export const PairRow: React.FC<{ i: number; k?: number; tilt?: number; size?: number; lineW?: number; style?: React.CSSProperties }> = ({ i, k = 1, tilt = 0, size = 40, lineW = 220, style }) => {
  const [l, r] = PAIRS[i];
  const w = size * 6.2;
  return (
    <div style={{ display: "flex", alignItems: "center", ...style }}>
      <div style={{ width: size * 1.3, fontFamily: F.song, fontSize: size * 0.8, color: C.red }}>{NUM[i]}</div>
      <div style={{ width: w, textAlign: "right", fontFamily: F.song, fontSize: size, color: C.ink, letterSpacing: 2, whiteSpace: "nowrap" }}>{l}</div>
      <svg width={lineW + 40} height={size * 1.6} style={{ margin: `0 ${size * 0.4}px`, overflow: "visible" }}>
        <g transform={`rotate(${tilt} ${(lineW + 40) / 2} ${size * 0.8})`}>
          <line x1={20} y1={size * 0.8} x2={20 + lineW * k} y2={size * 0.8} stroke={C.ink} strokeWidth={2} />
          <circle cx={20} cy={size * 0.8} r={size * 0.2} fill={C.ink} />
          <circle cx={20 + lineW} cy={size * 0.8} r={size * 0.2} fill={C.paper} stroke={C.ink} strokeWidth={2} opacity={k > 0.98 ? 1 : 0} />
        </g>
        <path d={`M${(lineW + 40) / 2 - 7},${size * 0.8 + 13} L${(lineW + 40) / 2},${size * 0.8 + 2} L${(lineW + 40) / 2 + 7},${size * 0.8 + 13} Z`} fill={C.red} opacity={k > 0.98 ? 1 : 0} />
      </svg>
      <div style={{ width: w, fontFamily: F.song, fontSize: size, color: C.ink, letterSpacing: 2, whiteSpace: "nowrap" }}>{r}</div>
    </div>
  );
};
