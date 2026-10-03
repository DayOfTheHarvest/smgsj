// Full trilingual Mass source: old crawl mass-times.html (22 rows).
// Office sign-off confirmed: keep old 22-row table (plan Sec 3).
// Live /main EN-only subset is intentionally NOT used as source.

import type { Lang } from '../config';
import massesData from './masses.json';
import scheduleInfo from './schedule-info.json';

import locationsData from './locations.json';

// Location names in each language (staff-managed in Decap: Mass schedule &
// presiders → Location names). `name` must match the English location used in
// the Mass list exactly — Decap offers it as a dropdown so it can't be mistyped.
const LOCALES: Record<string, Record<Lang, string>> = Object.fromEntries(
  ((locationsData as any).locations as Array<{ name: string; en: string; es: string; vi: string }>).map(
    (l) => [l.name, { en: l.en, es: l.es, vi: l.vi }],
  ),
);

export function locName(loc: string, lang: Lang): string {
  return LOCALES[loc]?.[lang] ?? loc;
}

// Day names per language, matching the parish's own Spanish/Vietnamese Mass
// pages. Applied at render time so the stored English times (used to match
// presiders) never change. Order matters: longest tokens first.
const DAY_TOKENS: Array<[string, string, string]> = [
  ['Mon-Fri', 'Lunes – Viernes', 'Thứ Hai – Thứ Sáu'],
  ['1st Friday', 'Primer Viernes', 'Thứ Sáu đầu tháng'],
  ['Monday', 'Lunes', 'Thứ Hai'],
  ['Tuesday', 'Martes', 'Thứ Ba'],
  ['Wednesday', 'Miércoles', 'Thứ Tư'],
  ['Thursday', 'Jueves', 'Thứ Năm'],
  ['Friday', 'Viernes', 'Thứ Sáu'],
  ['Saturday', 'Sábado', 'Thứ Bảy'],
  ['Sunday', 'Domingo', 'Chúa Nhật'],
];

export function dayName(time: string, lang: Lang): string {
  if (lang === 'en') return time;
  const col = lang === 'es' ? 1 : 2;
  let out = time;
  for (const [en, es, vi] of DAY_TOKENS) out = out.split(en).join(col === 1 ? es : vi);
  return out;
}

// Service (Mass type) labels per language. Fixed vocabulary like dayName.
export function serviceName(service: string, lang: Lang): string {
  const MAP: Record<string, Record<string, string>> = {
    Saturday: { en: 'Saturday', es: 'Sábado', vi: 'Thứ Bảy' },
    Sunday: { en: 'Sunday', es: 'Domingo', vi: 'Chúa Nhật' },
    Weekday: { en: 'Weekday', es: 'Entre semana', vi: 'Ngày thường' },
  };
  return MAP[service]?.[lang] ?? service;
}

export interface MassRow {
  service: string;
  /** Canonical day — Decap dropdown, never typed. Matches presiders via massKey. */
  day: string;
  /** Start time only, e.g. 4:00pm. Validated format, never typed freely. */
  time: string;
  /** Optional trailing marker, e.g. - Patio. Usually blank. */
  suffix?: string;
  lang: 'English' | 'Español' | 'Vietnamese' | 'Tagalog';
  location: string;
  /** Extra detail from the parish schedule graphic (e.g. Livestream). */
  note?: string;
}

/** Stable key shared with presiders.json — rebuilds the legacy time string. */
export function massKey(r: { day: string; time: string; suffix?: string }): string {
  return r.day + ' ' + r.time + (r.suffix ? ' ' + r.suffix : '');
}

// Schedule content lives in Decap-managed JSON so office staff (non-technical)
// can edit Mass times, locations, notes, confession and office hours at /admin.
// mass.ts keeps only the location translations (developer-owned).
export const MASS_ROWS: MassRow[] = (massesData as any).masses;
export const SCHEDULE_DISPLAY: { mode?: string; image?: string; link?: string } =
  (massesData as any).display ?? {};
export const CONFESSION: { day: Record<string, string>; time: Record<string, string> } = (
  scheduleInfo as any
).confession;
export const OFFICE_HOURS: Record<string, string> = (scheduleInfo as any).office;
