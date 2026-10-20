import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { C } from "./theme";

export const Paper: React.FC<{ children?: React.ReactNode; dim?: number }> = ({ children, dim = 0 }) => (
  <AbsoluteFill style={{ backgroundColor: C.paper }}>
    <Img src={staticFile("tex/paper.jpg")} style={{ position: "absolute", width: "100%", height: "100%" }} />
    {dim > 0 && <AbsoluteFill style={{ backgroundColor: C.ink, opacity: dim }} />}
    {children}
  </AbsoluteFill>
);

/** subtle animated film grain, multiplied over everything */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.07 }) => {
  const f = useCurrentFrame();
  const i = Math.floor(f / 2) % 6;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "overlay", opacity }}>
      <Img src={staticFile(`tex/grain${i}.png`)} style={{ width: "100%", height: "100%" }} />
    </AbsoluteFill>
  );
};
