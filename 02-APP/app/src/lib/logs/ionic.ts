// The Ionic battery's advertisement (electrical D-330, icu_channels IC24; 02-APP BL5's proof).
//
// D-330: the manufacturer data BEGINS with pack millivolts. The radio reads it as a
// little-endian uint16 in the first two bytes (du_radio/ionic_decode.h, ionic_adv_pack_mv) -
// the slot a BLE stack calls the company ID. tauri-plugin-blec, like every platform's
// stack, hands manufacturer data over as { companyId: bytes after it }, so here the pack
// millivolts ARE the key. The same plausibility window as the radio: 8.0-16.0 V for a 4S
// LiFePO4 pack, else no reading (0 is never "0 V"). Read only: nothing here connects to the
// pack, and its FEE7 / DFU service is never addressed (D-330).

/** the radio's BMS_NAME (du_radio.ino) - confirm at bring-up, as there */
export const BMS_NAME = 'IONIC';
const MIN_MV = 8000;
const MAX_MV = 16000;

export interface PackReading {
  mv: number;
  /** the bytes after the two millivolt bytes, as received */
  rest: number[];
}

/** Pack millivolts from an advertisement's manufacturer data, or null (ionic_adv_pack_mv). */
export function packMv(mfr: Record<number, number[]> | undefined): PackReading | null {
  for (const [k, rest] of Object.entries(mfr ?? {})) {
    const mv = Number(k);
    if (Number.isInteger(mv) && mv >= MIN_MV && mv <= MAX_MV) return { mv, rest };
  }
  return null;
}

export const looksIonic = (name: string) => name.toUpperCase().includes(BMS_NAME);

/** The manufacturer data as a scanner shows it: the company-ID slot as two bytes, little-endian, then the rest. */
export function mfrHex(mfr: Record<number, number[]> | undefined): string[] {
  return Object.entries(mfr ?? {}).map(([k, v]) =>
    [Number(k) & 0xff, (Number(k) >> 8) & 0xff, ...v].map((b) => b.toString(16).padStart(2, '0')).join(' '),
  );
}
