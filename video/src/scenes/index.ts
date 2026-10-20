import React from "react";
import { B1 } from "./B1";
import { B2 } from "./B2";
import { B3 } from "./B3";
import { B4 } from "./B4";
import { END } from "./END";
import { S0 } from "./S0";
import { S1 } from "./S1";
import { S2 } from "./S2";
import { S7 } from "./S7";
import { T0 } from "./T0";

export const SCENES: Record<string, React.FC> = { S0, T0, S1, S2, B1, B2, B3, B4, S7, END };
