import React from "react";
import { S0 } from "./S0";
import { S1 } from "./S1";
import { S2 } from "./S2";
import { T0 } from "./T0";
import { B1 } from "./B1";

export const SCENES: Record<string, React.FC> = { S0, T0, S1, S2, B1 };
