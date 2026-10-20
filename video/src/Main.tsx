import React from "react";
import { AbsoluteFill, Series, useVideoConfig } from "remotion";
import { Grain, Paper } from "./lib/Paper";
import { TL } from "./lib/timeline";
import { Narration, Subtitles } from "./lib/ui";
import { SCENES } from "./scenes";

export const Main: React.FC<{ subs: boolean }> = ({ subs }) => {
  const { fps } = useVideoConfig();
  return (
    <Paper>
      <Series>
        {TL.scenes.map((s) => {
          const Comp = SCENES[s.id];
          return (
            <Series.Sequence key={s.id} name={`${s.id} ${s.name}`} durationInFrames={s.dur} premountFor={fps}>
              <AbsoluteFill>{Comp ? <Comp /> : null}</AbsoluteFill>
            </Series.Sequence>
          );
        })}
      </Series>
      <Grain />
      {subs && <Subtitles />}
      <Narration />
    </Paper>
  );
};
