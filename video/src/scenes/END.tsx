import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, F, ramp } from "../lib/theme";
import { scene, TL } from "../lib/timeline";
import { Ink } from "../lib/ui";

const S = scene("END");
const M = TL as unknown as { meta: { members: string[]; team: string; source: string } };

export const END: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Ink at={6} d={26}>
        <div style={{ fontFamily: F.heavy, fontSize: 104, color: C.ink, letterSpacing: 22 }}>
          破立并举<span style={{ display: "inline-block", width: 56 }} />统筹兼顾
        </div>
      </Ink>
      <Ink at={18}>
        <div style={{ fontFamily: F.song, fontSize: 44, color: C.gray, letterSpacing: 12, marginTop: 26 }}>研读毛泽东《论十大关系》</div>
      </Ink>
      <div style={{ width: 700, height: 2, background: C.red, margin: "54px 0 46px", opacity: ramp(f, 30, 46) }} />
      <Ink at={40}>
        <div style={{ fontFamily: F.song, fontSize: 34, color: C.red, letterSpacing: 10, textAlign: "center" }}>{M.meta.team}</div>
      </Ink>
      <Ink at={50}>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 56, rowGap: 18, width: 1100, marginTop: 26 }}>
          {M.meta.members.map((n) => (
            <span key={n} style={{ fontFamily: F.song, fontSize: 38, color: C.ink, letterSpacing: 8, whiteSpace: "nowrap" }}>
              {n}
            </span>
          ))}
        </div>
      </Ink>
      <Ink at={66}>
        <div style={{ fontFamily: F.song, fontSize: 26, color: C.gray, letterSpacing: 4, marginTop: 60 }}>文本依据：{M.meta.source}</div>
      </Ink>
      <AbsoluteFill style={{ backgroundColor: "#0E0D0B", opacity: ramp(f, S.dur - 40, S.dur - 4) }} />
    </AbsoluteFill>
  );
};
