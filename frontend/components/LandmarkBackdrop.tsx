/**
 * Decorative layer of minimal Iranian landmark line-art that drifts along
 * the viewport diagonal, bottom-left to top-right. Purely ambient: it sits
 * on a negative z-index so every card, panel and the header paint over it,
 * and it is hidden from assistive tech.
 *
 * Every shape shares one motion vector (see the landmark-drift keyframes),
 * which traces the viewport diagonal. Coverage of the rest of the screen
 * comes from the lane system described on LANES below.
 */

type Shape = {
  key: string;
  viewBox: string;
  paths: string[];
};

const MILAD = [
  "M12 120 L19 96 L41 96 L48 120",
  "M16 108 H44",
  "M26 96 L27 58 M34 96 L33 58",
  "M27 58 C11 51 11 39 30 33 C49 39 49 51 33 58",
  "M24 45 H36",
  "M28 33 V25 H32 V33",
  "M30 25 V4",
];

const AZADI = [
  "M2 100 L10 58 Q17 30 40 17",
  "M78 100 L70 58 Q63 30 40 17",
  "M24 100 L29 60 Q34 42 40 35 Q46 42 51 60 L56 100",
  "M33 17 V6 H47 V17",
  "M0 100 H80",
];

const PERSEPOLIS = [
  "M0 90 H110",
  "M7 84 H103",
  "M14 78 H96",
  "M25 78 V28 M31 78 V28",
  "M52 78 V28 M58 78 V28",
  "M79 78 V28 M85 78 V28",
  "M22 28 H34 M49 28 H61 M76 28 H88",
  "M18 21 H92 M18 14 H92",
];

const HAFEZIEH = [
  "M4 90 H96",
  "M11 84 H89",
  "M20 84 V45 M32 84 V45 M44 84 V45 M56 84 V45 M68 84 V45 M80 84 V45",
  "M13 45 H87 M13 38 H87",
  "M25 38 Q50 -12 75 38",
  "M50 13 V3",
];

const KHAYYAM = [
  "M14 94 H76 M8 100 H82",
  "M18 94 L34 18",
  "M72 94 L56 18",
  "M34 18 L45 5 L56 18",
  "M23 72 L45 60 L67 72",
  "M27 55 L45 44 L63 55",
  "M30 40 L45 31 L60 40",
];

const SIOSEPOL = [
  "M0 30 H130 M0 24 H130",
  "M4 48 V38 A8 8 0 0 1 20 38 V48",
  "M26 48 V38 A8 8 0 0 1 42 38 V48",
  "M48 48 V38 A8 8 0 0 1 64 38 V48",
  "M70 48 V38 A8 8 0 0 1 86 38 V48",
  "M92 48 V38 A8 8 0 0 1 108 38 V48",
  "M114 48 V38 A8 8 0 0 1 130 38 V48",
  "M0 48 H130",
  "M58 24 V12 H74 V24",
  "M62 24 V18 A4 4 0 0 1 70 18 V24",
];

const DOME = [
  "M6 100 H94",
  "M24 100 V60 H76 V100",
  "M41 100 V76 Q45 62 50 57 Q55 62 59 76 V100",
  "M33 60 V54 H67 V60",
  "M31 54 Q31 28 50 16 Q69 28 69 54",
  "M50 16 V7",
  "M13 100 V32 M19 100 V32 M11 32 H21 M16 32 V24",
  "M81 100 V32 M87 100 V32 M79 32 H89 M84 32 V24",
];

const SHAPES: Shape[] = [
  { key: "milad", viewBox: "0 0 60 120", paths: MILAD },
  { key: "azadi", viewBox: "0 0 80 100", paths: AZADI },
  { key: "persepolis", viewBox: "0 0 110 90", paths: PERSEPOLIS },
  { key: "hafezieh", viewBox: "0 0 100 90", paths: HAFEZIEH },
  { key: "khayyam", viewBox: "0 0 90 100", paths: KHAYYAM },
  { key: "siosepol", viewBox: "0 0 130 60", paths: SIOSEPOL },
  { key: "dome", viewBox: "0 0 100 100", paths: DOME },
];

/**
 * A lane is a line parallel to the shared drift vector. `lateral` slides the
 * lane perpendicular to it — negative towards the top-left corner, positive
 * towards the bottom-right — so the lanes fan out and together sweep the
 * whole viewport while each shape still travels the same diagonal.
 *
 * `phases` are entry points along a lane as a fraction of one cycle, applied
 * as negative delays so the shapes are already distributed at load. Outer
 * lanes only clip a corner of the screen and so spend most of their cycle
 * out of frame; they carry an extra shape to stay populated.
 */
const LANES = [
  { lateral: -45, width: 96, duration: 108, phases: [0.08, 0.42, 0.74] },
  { lateral: -34, width: 128, duration: 96, phases: [0.18, 0.62, 0.88] },
  { lateral: -22, width: 108, duration: 112, phases: [0.04, 0.5, 0.78] },
  { lateral: -11, width: 148, duration: 100, phases: [0.14, 0.47, 0.8] },
  { lateral: 0, width: 116, duration: 106, phases: [0.05, 0.38, 0.71] },
  { lateral: 11, width: 136, duration: 94, phases: [0.2, 0.53, 0.86] },
  { lateral: 22, width: 104, duration: 110, phases: [0.22, 0.68, 0.92] },
  { lateral: 34, width: 124, duration: 98, phases: [0.1, 0.46, 0.78] },
  { lateral: 45, width: 92, duration: 104, phases: [0.26, 0.6, 0.9] },
];

/** Off-screen corner every lane is measured from, in percent. */
const START_LEFT = -20;
const START_BOTTOM = -20;

const DRIFTERS = LANES.flatMap((lane, laneIndex) =>
  lane.phases.map((phase, phaseIndex) => ({
    id: `${laneIndex}-${phaseIndex}`,
    // Striding by 3 keeps neighbouring lanes from showing the same landmark.
    shape: SHAPES[(laneIndex * 3 + phaseIndex) % SHAPES.length],
    width: lane.width,
    left: START_LEFT + lane.lateral,
    bottom: START_BOTTOM - lane.lateral,
    duration: lane.duration,
    delay: -(phase * lane.duration),
  })),
);

export default function LandmarkBackdrop() {
  return (
    <div className="landmark-backdrop" aria-hidden="true">
      {DRIFTERS.map((drifter) => (
        <svg
          key={drifter.id}
          className="landmark"
          viewBox={drifter.shape.viewBox}
          width={drifter.width}
          fill="none"
          stroke="currentColor"
          strokeWidth={4}
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            left: `${drifter.left}%`,
            bottom: `${drifter.bottom}%`,
            animationDuration: `${drifter.duration}s`,
            animationDelay: `${drifter.delay}s`,
          }}
        >
          {drifter.shape.paths.map((d, index) => (
            <path key={index} d={d} vectorEffect="non-scaling-stroke" />
          ))}
        </svg>
      ))}
    </div>
  );
}
