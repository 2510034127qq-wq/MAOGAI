import React from "react";
import { Composition, Folder } from "remotion";
import "./lib/theme";
import { Main } from "./Main";
import { Paper } from "./lib/Paper";
import { TL } from "./lib/timeline";
import { SCENES } from "./scenes";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Main" component={Main} width={1920} height={1080} fps={30} durationInFrames={TL.total} defaultProps={{ subs: true }} />
    <Composition id="MainClean" component={Main} width={1920} height={1080} fps={30} durationInFrames={TL.total} defaultProps={{ subs: false }} />
    <Folder name="Scenes">
      {TL.scenes
        .filter((s) => SCENES[s.id])
        .map((s) => {
          const Comp = SCENES[s.id];
          const Wrapped: React.FC = () => (
            <Paper>
              <Comp />
            </Paper>
          );
          return <Composition key={s.id} id={s.id} component={Wrapped} width={1920} height={1080} fps={30} durationInFrames={s.dur} />;
        })}
    </Folder>
  </>
);
