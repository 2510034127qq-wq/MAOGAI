import { Easing, interpolate } from "remotion";
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const C = {
  paper: "#EDE5D4",
  paper2: "#E4D9C3",
  paperHi: "#F4EEE1",
  ink: "#1C1A17",
  gray: "#6B655B",
  faint: "#A39B8B",
  red: "#B5302A",
  brass: "#8A6A3B",
};

export const F = {
  song: "STSong, serif",
  heavy: "SongHeavy, serif",
  kai: "STKai, serif",
  serif: "NotoSerifSC, serif",
};

loadFont({ family: "STSong", url: staticFile("fonts/STSONG.TTF") });
loadFont({ family: "STKai", url: staticFile("fonts/STKAITI.TTF") });
loadFont({ family: "SongHeavy", url: staticFile("fonts/SourceHanSerifSC-Heavy.ttf") });
loadFont({ family: "NotoSerifSC", url: staticFile("fonts/NotoSerifSC-VF.ttf"), weight: "200 900" });

export const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const io = Easing.bezier(0.65, 0, 0.35, 1);

export const ramp = (f: number, a: number, b: number, o0 = 0, o1 = 1, e = ease) =>
  interpolate(f, [a, b], [o0, o1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: e });

/** opacity envelope: fade in at a, hold, fade out ending at b */
export const env = (f: number, a: number, b: number, fi = 12, fo = 12) =>
  Math.min(ramp(f, a, a + fi), 1 - ramp(f, b - fo, b, 0, 1, io));

export const W = 1920;
export const H = 1080;
