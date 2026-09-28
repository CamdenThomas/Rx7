/*
 * test_dcu.cpp — desktop verification of the DCU logic (F-001)
 *
 * Compiles the REAL climate.h + panel.h + can_map.h from ../dcu. Covers the
 * seat interlock (D-073), comfort gating, keypad edges, servo mapping, the
 * SD climate-memory CRC, and F-017: the key matrix, 0x400, wake and replay,
 * the release select (D-370), knobs, windows (D-363), mirrors (D-359,
 * D-360), one servo at a time (D-379), the NTCs, current and mirror heat.
 *
 * Build (g++ on PATH):
 *   g++ test_dcu.cpp -o test_dcu -std=c++17 -O2 -I../dcu && ./test_dcu
 */
#include <cstdio>
#include <cstring>
#include "climate.h"
#include "panel.h"

static int g_pass = 0, g_fail = 0;
#define CHECK(cond, msg) do { \
    if (cond) g_pass++; \
    else { g_fail++; printf("  FAIL %s:%d  %s\n", __FILE__, __LINE__, msg); } \
} while (0)

static dcu_state_t fresh() {
    dcu_state_t s;
    memset(&s, 0, sizeof s);
    mem_defaults(&s.mem);
    return s;
}

int main() {
    printf("-- DCU logic verification --\n");

    /* ============ 1. seat interlock (D-073) — heat wins ============ */
    {
        dcu_state_t s = fresh();
        s.mem.seat_heat = 0x02;            /* driver heat level 2   */
        s.mem.seat_cool = 0x01;            /* driver cool level 1   */
        enforce_seat_interlock(&s);
        CHECK(s.mem.seat_cool == 0, "driver cool cleared when driver heat on");
        CHECK(s.comfort_on[CMF_SEAT_HEAT_DRV] == 1 && s.comfort_on[CMF_SEAT_COOL_DRV] == 0,
              "driver channels: heat on, cool off");

        s = fresh();
        s.mem.seat_heat = 0x08;            /* passenger heat        */
        s.mem.seat_cool = 0x04 | 0x01;     /* passenger + driver cool */
        enforce_seat_interlock(&s);
        CHECK(s.mem.seat_cool == 0x01, "passenger cool cleared, driver cool untouched");
        CHECK(s.comfort_on[CMF_SEAT_COOL_DRV] == 1 && s.comfort_on[CMF_SEAT_COOL_PASS] == 0
              && s.comfort_on[CMF_SEAT_HEAT_PASS] == 1,
              "flags follow per-seat, not global");

        /* exhaustive: no (heat,cool) input ever leaves both on for a seat */
        bool never = true;
        for (int h = 0; h < 16 && never; h++)
            for (int c = 0; c < 16 && never; c++) {
                s = fresh();
                s.mem.seat_heat = (uint8_t)h; s.mem.seat_cool = (uint8_t)c;
                enforce_seat_interlock(&s);
                if ((s.mem.seat_heat & 3) && (s.mem.seat_cool & 3)) never = false;
                if ((s.mem.seat_heat & 0x0C) && (s.mem.seat_cool & 0x0C)) never = false;
            }
        CHECK(never, "all 256 heat/cool combos: never both on one seat");
    }

    /* ================= 1b. blower duty (D-308, F-012) ================= */
    {
        CHECK(blower_duty_pct(0) == 0,   "blower level 0 is 0 % - off is off");
        CHECK(blower_duty_pct(1) == 33 && blower_duty_pct(2) == 67, "levels 1-2 are 33 / 67 %");
        CHECK(blower_duty_pct(3) == 100, "level 3 is 100 %");
        CHECK(blower_duty_pct(9) == 100, "an out-of-range level clamps to 100 %, never wraps");
        CHECK(CMF_COUNT == 5, "five comfort channels - nozzles and de-icer cancelled (D-329)");
    }

    /* ================= 2. comfort gating ================= */
    {
        dcu_state_t s = fresh();
        s.key_pos = KEY_RUN; s.pmu_alive = 1;
        CHECK(comfort_permitted(&s) == 1, "RUN + PMU alive permits comfort");
        s.pmu_alive = 0;
        CHECK(comfort_permitted(&s) == 0, "dead PMU blocks comfort");
        s.pmu_alive = 1; s.key_pos = KEY_ACC;
        CHECK(comfort_permitted(&s) == 0, "ACC blocks comfort");
        s.key_pos = KEY_START;
        CHECK(comfort_permitted(&s) == 0, "cranking blocks comfort");
    }

    /* ================= 3. keypad edges ================= */
    {
        dcu_state_t s = fresh();               /* defaults: VENT, 21 C */
        apply_keypad(&s, KP_MODE);
        CHECK(s.mem.mode == CLIM_HEAT, "VENT -> HEAT");
        apply_keypad(&s, KP_MODE);
        CHECK(s.mem.mode == CLIM_DEFROST, "HEAT -> DEFROST");
        apply_keypad(&s, KP_MODE);
        CHECK(s.mem.mode == CLIM_VENT, "DEFROST wraps to VENT");
        s.mem.mode = CLIM_AC;                  /* out-of-cycle (corrupt/AC) */
        apply_keypad(&s, KP_MODE);
        CHECK(s.mem.mode == CLIM_VENT, "out-of-cycle mode lands on VENT");
        s.mem.mode = CLIM_OFF;
        apply_keypad(&s, KP_MODE);
        CHECK(s.mem.mode == CLIM_VENT, "OFF lands on VENT");

        s = fresh();
        for (int i = 0; i < 20; i++) apply_keypad(&s, KP_TEMP_UP);
        CHECK(s.mem.target_c == 30, "temp clamps at 30");
        for (int i = 0; i < 40; i++) apply_keypad(&s, KP_TEMP_DN);
        CHECK(s.mem.target_c == 16, "temp clamps at 16");

        uint8_t r0 = s.mem.recirc;
        apply_keypad(&s, KP_RECIRC);
        CHECK(s.mem.recirc == (r0 ^ 1), "recirc toggles");
        apply_keypad(&s, KP_RECIRC);
        CHECK(s.mem.recirc == r0, "recirc toggles back");
    }

    /* ================= 4. servo mapping ================= */
    {
        dcu_state_t s = fresh();               /* cal 1000..2000 us */
        s.mem.mode = CLIM_VENT;    mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_MODE].us_now == 1000, "VENT -> mode door min");
        s.mem.mode = CLIM_HEAT;    mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_MODE].us_now == 1500, "HEAT -> mode door mid");
        s.mem.mode = CLIM_DEFROST; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_MODE].us_now == 2000, "DEFROST -> mode door max");
        uint16_t held = s.mem.cal[SRV_MODE].us_now;
        s.mem.mode = CLIM_OFF;     mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_MODE].us_now == held, "OFF leaves the door in place");

        s.mem.target_c = 16; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_BLEND].us_now == 1000, "16 C -> blend min");
        s.mem.target_c = 30; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_BLEND].us_now == 2000, "30 C -> blend max");
        s.mem.target_c = 23; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_BLEND].us_now == 1500, "23 C -> blend mid");
        s.mem.target_c = 99; mode_to_servos(&s);   /* corrupt value */
        CHECK(s.mem.cal[SRV_BLEND].us_now == 2000, "target clamps before mapping");

        /* commanded pulse can never leave the calibrated window */
        bool inWin = true;
        for (int m = 0; m <= CLIM_AC; m++)
            for (int t = 0; t < 256; t++) {
                s.mem.mode = (uint8_t)m; s.mem.target_c = (uint8_t)t;
                s.mem.recirc = (uint8_t)(t & 1);
                mode_to_servos(&s);
                for (int v = 0; v < SRV_COUNT; v++)
                    if (s.mem.cal[v].us_now < 1000 || s.mem.cal[v].us_now > 2000) inWin = false;
            }
        CHECK(inWin, "all modes x all targets: pulses stay in 1000..2000");

        s.mem.recirc = 1; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_RECIRC].us_now == 2000, "recirc -> door max");
        s.mem.recirc = 0; mode_to_servos(&s);
        CHECK(s.mem.cal[SRV_RECIRC].us_now == 1000, "fresh -> door min");
    }

    /* ================= 5. climate-memory CRC ================= */
    {
        climate_mem_t m; mem_defaults(&m);
        m.crc = mem_crc(&m);
        CHECK(m.crc == mem_crc(&m), "crc field itself is excluded from the sum");

        climate_mem_t bad = m;
        bad.target_c ^= 0x40;                  /* one flipped bit */
        CHECK(mem_crc(&bad) != m.crc, "single-bit corruption changes the CRC");

        uint8_t blob[sizeof(climate_mem_t)];   /* SD round-trip */
        memcpy(blob, &m, sizeof m);
        climate_mem_t back; memcpy(&back, blob, sizeof back);
        CHECK(back.crc == mem_crc(&back), "byte round-trip keeps a valid CRC");

        CHECK(m.mode == CLIM_VENT && m.target_c == 21, "defaults: VENT, 21 C");
    }

    /* ================= 6. key matrix and debounce (D-380, F-016) ================= */
    {
        CHECK(matrix_bit(0, 0) == PK_DEFOG && matrix_bit(0, 1) == PK_HATCH && matrix_bit(0, 2) == PK_FUEL_DOOR,
              "ROW1: defog, hatch, fuel door");
        CHECK(matrix_bit(1, 0) == PK_HVAC_MODE && matrix_bit(1, 1) == PK_RECIRC && matrix_bit(1, 2) == PK_WIN_DRV_UP,
              "ROW2: mode, recirc, DRV up");
        CHECK(matrix_bit(2, 0) == PK_WIN_DRV_DN && matrix_bit(2, 1) == PK_WIN_PASS_UP && matrix_bit(2, 2) == PK_WIN_PASS_DN,
              "ROW3: DRV down, PASS up, PASS down");

        panel_t p; memset(&p, 0, sizeof p);
        uint16_t e = 0;
        for (int i = 0; i < KEY_DEBOUNCE_SCANS - 1; i++) e |= keys_debounce(&p, PK_RECIRC);
        CHECK(e == 0 && p.phys == 0, "a key is not down before the debounce");
        e = keys_debounce(&p, PK_RECIRC);
        CHECK(e == PK_RECIRC && p.phys == PK_RECIRC, "down after the debounce, one edge");
        CHECK(keys_debounce(&p, 0) == 0 && p.phys == PK_RECIRC, "one bounce open does not release it");
        e = 0;
        for (int i = 0; i < 20; i++) e |= keys_debounce(&p, (i & 1) ? PK_RECIRC : 0);
        CHECK(e == 0, "chatter makes no second edge");
    }

    /* ================= 7. 0x400: held, heartbeat, wake and replay (D-355) ================= */
    {
        panel_t p; memset(&p, 0, sizeof p);
        uint16_t down = 0, held = 0; uint32_t t = 10000;
        for (int i = 0; i < 10; i++, t += 5) panel_keys_step(&p, PK_WIN_DRV_UP, 1, t, &down, &held);
        CHECK(down == PK_WIN_DRV_UP && held == 0, "window key down, not yet held");
        for (int i = 0; i < 200; i++, t += 5) panel_keys_step(&p, PK_WIN_DRV_UP, 1, t, &down, &held);
        CHECK(held == PK_WIN_DRV_UP, "held after 1 s");

        keys_tx_t tx; memset(&tx, 0, sizeof tx); panel_keys_t f;
        CHECK(panel_frame_due(&tx, 1, 0, 0, &f) == 1 && f.down == 1 && f.counter == 0, "first frame goes");
        CHECK(panel_frame_due(&tx, 1, 0, 100, &f) == 0, "no change, no frame");
        CHECK(panel_frame_due(&tx, 3, 0, 150, &f) == 1 && f.counter == 1, "a change goes at once");
        CHECK(panel_frame_due(&tx, 3, 0, 649, &f) == 0 && panel_frame_due(&tx, 3, 0, 650, &f) == 1,
              "2 Hz heartbeat");
        CHECK(sizeof(panel_keys_t) == CAN_MSG_LEN, "0x400 payload is 8 bytes");

        /* asleep: a defog tap wakes the PMU and is replayed once it answers */
        memset(&p, 0, sizeof p); t = 20000;
        for (int i = 0; i < 6; i++, t += 5) panel_keys_step(&p, PK_DEFOG, 0, t, &down, &held);
        CHECK(p.wake_req == 1 && down == 0, "asleep: wake pulled, the edge key held back");
        for (int i = 0; i < 6; i++, t += 5) panel_keys_step(&p, 0, 0, t, &down, &held);
        CHECK(p.wake_req == 1 && p.latched == PK_DEFOG, "released before the PMU woke: latched");
        panel_keys_step(&p, 0, 1, t, &down, &held); t += 5;
        CHECK(p.wake_req == 0 && down == PK_DEFOG, "PMU alive: the tap is replayed");
        for (int i = 0; i < REPLAY_MS / 5 + 1; i++, t += 5) panel_keys_step(&p, 0, 1, t, &down, &held);
        CHECK(down == 0, "and released after the replay");

        /* a PMU that never answers drops the latched press */
        memset(&p, 0, sizeof p); t = 30000;
        for (int i = 0; i < 6; i++, t += 5) panel_keys_step(&p, PK_HATCH, 0, t, &down, &held);
        for (int i = 0; i < 6; i++, t += 5) panel_keys_step(&p, 0, 0, t, &down, &held);
        t += WAKE_REQ_MAX_MS;
        panel_keys_step(&p, 0, 0, t, &down, &held);
        CHECK(p.wake_req == 0 && p.latched == 0, "no answer in 3 s: wake and the press dropped");
        panel_keys_step(&p, 0, 1, t + 5, &down, &held);
        CHECK(down == 0 && p.rel_sel == 0, "a late PMU never pops the hatch");

        /* a CAN hiccup with defog held makes no second edge */
        memset(&p, 0, sizeof p); t = 40000;
        for (int i = 0; i < 6; i++, t += 5) panel_keys_step(&p, PK_DEFOG, 1, t, &down, &held);
        panel_keys_step(&p, PK_DEFOG, 0, t, &down, &held); t += 5;
        CHECK(down == PK_DEFOG, "PMU lost with the key held: it stays down, no new edge later");

        CHECK(sleep_due(&p, 0, DCU_SLEEP_AFTER_MS) == 0, "no sleep with a key down");
        panel_t q; memset(&q, 0, sizeof q);
        CHECK(sleep_due(&q, 0, DCU_SLEEP_AFTER_MS) == 1 && sleep_due(&q, 1, DCU_SLEEP_AFTER_MS) == 0
              && sleep_due(&q, 0, DCU_SLEEP_AFTER_MS - 1) == 0, "sleep: PMU gone, idle 30 s");
    }

    /* ================= 8. release select (D-370) ================= */
    {
        panel_t p; memset(&p, 0, sizeof p);
        uint16_t down = 0, held = 0; uint32_t t = 50000;
        for (int i = 0; i < 4; i++, t += 5) panel_keys_step(&p, PK_HATCH, 1, t, &down, &held);
        CHECK(p.rel_sel == PK_HATCH && down == PK_HATCH, "hatch: K3 selected in the same scan the edge goes");
        for (int i = 0; i < 4; i++, t += 5) panel_keys_step(&p, PK_HATCH | PK_FUEL_DOOR, 1, t, &down, &held);
        CHECK(p.rel_sel == PK_HATCH && !(down & PK_FUEL_DOOR), "fuel door during the hatch hold: refused, kept off 0x400");
        for (int i = 0; i < 4; i++, t += 5) panel_keys_step(&p, PK_HATCH, 1, t, &down, &held);
        for (int i = 0; i < 4; i++, t += 5) panel_keys_step(&p, 0, 1, t, &down, &held);
        CHECK(p.rel_sel == PK_HATCH, "held through the pulse after the key is let go");
        t += RELEASE_HOLD_MS;
        panel_keys_step(&p, 0, 1, t, &down, &held);
        CHECK(p.rel_sel == 0, "released after the hold");

        memset(&p, 0, sizeof p);
        for (int i = 0; i < 4; i++, t += 5) panel_keys_step(&p, PK_HATCH | PK_FUEL_DOOR, 1, t, &down, &held);
        CHECK(p.rel_sel == 0 && !(down & PK_RELEASE), "both at once: neither, and the PMU sees neither");

        /* exhaustive: over random key sequences the select is never both, and
         * a release edge reaches 0x400 only with its own relay selected */
        bool ok = true; uint32_t seed = 12345;
        memset(&p, 0, sizeof p);
        uint16_t prev_down = 0;
        for (int i = 0; i < 200000 && ok; i++, t += 5) {
            seed = seed * 1103515245u + 12345u;
            uint16_t raw = (uint16_t)((seed >> 16) & PK_RELEASE);
            uint8_t alive = ((seed >> 8) & 31) != 0;
            panel_keys_step(&p, raw, alive, t, &down, &held);
            if (p.rel_sel != 0 && p.rel_sel != PK_HATCH && p.rel_sel != PK_FUEL_DOOR) ok = false;
            uint16_t edge = (uint16_t)(down & ~prev_down & PK_RELEASE);
            if (edge && edge != p.rel_sel) ok = false;
            prev_down = down;
        }
        CHECK(ok, "200k random scans: one relay at most, every release edge steered");
    }

    /* ================= 9. encoders and knobs (SN20, D-073) ================= */
    {
        enc_t e; memset(&e, 0, sizeof e); e.ab = 3;
        const uint8_t cw[4] = { 2, 0, 1, 3 };           /* 11 -> 10 -> 00 -> 01 -> 11 */
        int d = 0;
        for (int k = 0; k < 4; k++) d += enc_step(&e, cw[k]);
        CHECK(d == 1, "one clockwise detent");
        for (int k = 3; k >= 0; k--) d += enc_step(&e, k ? cw[k - 1] : 3);
        CHECK(d == 0, "one anticlockwise detent back");
        d = 0;
        for (int k = 0; k < 50; k++) { d += enc_step(&e, 2); d += enc_step(&e, 3); }
        CHECK(d == 0, "contact bounce on one edge adds nothing");

        dcu_state_t s = fresh();
        panel_apply(&s, 0, 0, 0, 2, 0);
        CHECK((s.mem.seat_heat & 3) == 2 && (s.mem.seat_cool & 3) == 0, "driver knob +2: heat 2");
        panel_apply(&s, 0, 0, 0, -4, 0);
        CHECK((s.mem.seat_heat & 3) == 0 && (s.mem.seat_cool & 3) == 2, "then -4: through OFF to cool 2");
        panel_apply(&s, 0, 0, 0, -9, 5);
        CHECK((s.mem.seat_cool & 3) == 3 && ((s.mem.seat_heat >> 2) & 3) == 3, "clamped at cool 3 / heat 3");
        bool never = true;
        for (int a = -8; a <= 8; a++) for (int b = -8; b <= 8; b++) {
            panel_apply(&s, 0, 0, 0, a, b);
            if ((s.mem.seat_heat & 3) && (s.mem.seat_cool & 3)) never = false;
            if ((s.mem.seat_heat & 0xC) && (s.mem.seat_cool & 0xC)) never = false;
        }
        CHECK(never, "no knob sequence heats and cools one seat");

        s = fresh();
        panel_apply(&s, 0, 5, 0, 0, 0);
        CHECK(s.mem.blower == 3, "fan clamps at 3");
        panel_apply(&s, 0, -9, 0, 0, 0);
        CHECK(s.mem.blower == 0, "fan clamps at off");
        panel_apply(&s, 0, 0, 3, 0, 0);
        CHECK(s.mem.target_c == 24, "temperature knob: one degree a detent");
        panel_apply(&s, PK_HVAC_MODE | PK_RECIRC, 0, 0, 0, 0);
        CHECK(s.mem.mode == CLIM_HEAT && s.mem.recirc == 1, "mode and recirc keys");
        panel_apply(&s, PK_DEFOG | PK_HATCH, 0, 0, 0, 0);
        CHECK(s.mem.mode == CLIM_HEAT, "PMU keys do nothing locally");
    }

    /* ================= 10. windows (SN22, D-363) ================= */
    {
        window_t w; memset(&w, 0, sizeof w);
        uint8_t up, dn; uint32_t t = 60000;
        window_step(&w, 1, 0, 1, t, &up, &dn);
        CHECK(up == 1 && dn == 0, "up key: up relay");
        window_step(&w, 0, 1, 1, t += 5, &up, &dn);
        CHECK(up == 0 && dn == 0, "reversal: both at rest first");
        window_step(&w, 0, 1, 1, t += WINDOW_DEAD_MS - 10, &up, &dn);
        CHECK(dn == 0, "still resting inside the dead time");
        window_step(&w, 0, 1, 1, t += 10, &up, &dn);
        CHECK(dn == 1 && up == 0, "then down");
        window_step(&w, 1, 1, 1, t += 5, &up, &dn);
        CHECK(up == 0 && dn == 0, "both keys: stop");
        window_step(&w, 1, 0, 0, t += 500, &up, &dn);
        CHECK(up == 0, "not permitted: nothing");
        window_step(&w, 1, 0, 1, t += 5, &up, &dn);
        window_step(&w, 1, 0, 1, t += WINDOW_MAX_RUN_MS, &up, &dn);
        CHECK(up == 0, "held past the run limit: stops");
        window_step(&w, 1, 0, 1, t += 500, &up, &dn);
        CHECK(up == 0, "and stays stopped until let go");
        window_step(&w, 0, 0, 1, t += 5, &up, &dn);
        window_step(&w, 1, 0, 1, t += WINDOW_DEAD_MS, &up, &dn);
        CHECK(up == 1, "let go and pressed again: runs");

        bool never = true; uint32_t seed = 777;
        memset(&w, 0, sizeof w);
        for (int i = 0; i < 100000 && never; i++) {
            seed = seed * 1103515245u + 12345u;
            window_step(&w, (seed >> 16) & 1, (seed >> 17) & 1, ((seed >> 18) & 7) != 0,
                        t += (seed >> 20) & 63, &up, &dn);
            if (up && dn) never = false;
        }
        CHECK(never, "100k random steps: up and down never together");
    }

    /* ================= 11. mirrors (SN17, D-359, D-360) ================= */
    {
        stick_cal_t c; stick_defaults(&c);
        uint8_t axis; int8_t dir;
        stick_read(&c, 2048 + 300, 2048, &axis, &dir);
        CHECK(axis == AXIS_NONE, "inside the dead band: nothing");
        stick_read(&c, 4000, 2600, &axis, &dir);
        CHECK(axis == AXIS_X && dir == MIRROR_SIGN_X, "the larger deflection wins");
        stick_read(&c, 2048, 100, &axis, &dir);
        CHECK(axis == AXIS_Y && dir == -MIRROR_SIGN_Y, "Y the other way");

        mirror_t m; memset(&m, 0, sizeof m); mirror_out_t o; uint32_t t = 70000;
        mirror_step(&m, 0, AXIS_X, 1, 1, t, &o);
        CHECK(o.left == HB_HIGH && o.common == HB_LOW && o.right == HB_OFF, "left side by default, right open");
        CHECK(o.clutch == (AXIS_X == MIRROR_CLUTCH_AXIS), "clutch follows the axis");
        mirror_step(&m, 0, AXIS_X, -1, 1, t += 5, &o);
        CHECK(o.left == HB_OFF && o.common == HB_OFF, "reversal: bridges open first");
        mirror_step(&m, 0, AXIS_X, -1, 1, t += MIRROR_DEAD_MS, &o);
        CHECK(o.left == HB_LOW && o.common == HB_HIGH, "then reversed polarity");
        mirror_step(&m, PK_MIRROR_PRESS, AXIS_Y, 1, 1, t += 5, &o);
        CHECK(m.side == MIRROR_RIGHT && o.left == HB_OFF && o.right == HB_OFF, "press: side toggles, all stop");
        CHECK(o.clutch == (AXIS_Y == MIRROR_CLUTCH_AXIS), "clutch settles during the dead time");
        mirror_step(&m, 0, AXIS_Y, 1, 1, t += MIRROR_DEAD_MS, &o);
        CHECK(o.right == HB_HIGH && o.left == HB_OFF, "right mirror moves, left open");
        mirror_step(&m, 0, AXIS_Y, 1, 0, t += 5, &o);
        CHECK(o.right == HB_OFF && o.common == HB_OFF && o.clutch == 0, "not permitted: everything open");

        bool ok = true; uint32_t seed = 4242;
        memset(&m, 0, sizeof m);
        for (int i = 0; i < 100000 && ok; i++) {
            seed = seed * 1103515245u + 12345u;
            uint8_t ax = (uint8_t)((seed >> 16) % 3);
            int8_t  dr = ax ? (((seed >> 18) & 1) ? 1 : -1) : 0;
            mirror_step(&m, ((seed >> 19) & 15) == 0 ? PK_MIRROR_PRESS : 0, ax, dr,
                        ((seed >> 23) & 7) != 0, t += (seed >> 24) & 31, &o);
            if (o.left != HB_OFF && o.right != HB_OFF) ok = false;          /* one mirror at a time */
            if ((o.left != HB_OFF || o.right != HB_OFF) == (o.common == HB_OFF)) ok = false;
            if (o.common != HB_OFF && (o.left == o.common || o.right == o.common)) ok = false;
        }
        CHECK(ok, "100k random steps: one side driven, always against the common");
    }

    /* ================= 12. servos one at a time (D-379) ================= */
    {
        dcu_state_t s = fresh();
        mode_to_servos(&s);                    /* targets 1000 / 1357 / 1000 us */
        servo_seq_t q; memset(&q, 0, sizeof q);
        uint32_t t = 80000;
        CHECK(servo_seq_step(&q, s.mem.cal, t) >= 0, "first servo moves");
        CHECK(servo_seq_step(&q, s.mem.cal, t + SERVO_SETTLE_MS - 1) == -1, "the next waits for the settle");
        CHECK(servo_seq_step(&q, s.mem.cal, t + SERVO_SETTLE_MS) >= 0, "then moves");
        CHECK(servo_seq_step(&q, s.mem.cal, t + 2 * SERVO_SETTLE_MS) >= 0, "third");
        CHECK(servo_seq_step(&q, s.mem.cal, t + 3 * SERVO_SETTLE_MS) == -1, "nothing left to move");
        bool same = true;
        for (int i = 0; i < SRV_COUNT; i++) if (q.applied[i] != s.mem.cal[i].us_now) same = false;
        CHECK(same, "every servo reached its target");
    }

    /* ================= 13. analog inputs and mirror heat ================= */
    {
        CHECK(ntc_to_c(2048) == 25, "NTC at mid-scale reads 25 C");
        CHECK(ntc_to_c(0) == TEMP_INVALID && ntc_to_c(4095) == TEMP_INVALID, "short and open read blank");
        CHECK(ntc_to_c(1000) > 25 && ntc_to_c(3000) < 25, "hotter pulls the divider down");
        CHECK(comfort_current_ca(1241, 0) == 1000, "1.0 V at the ADC is 10.00 A");
        CHECK(comfort_current_ca(50, 60) == 0, "below the zero reads 0, never wraps");

        pmu_outputs_t m; memset(&m, 0, sizeof m);
        m.out_state[0] = 0x08;
        CHECK(pmu_out_on(&m, PMU_OUT_DEFOG) == 1 && pmu_out_on(&m, 0) == 0, "O4 is 0x120 byte 2 bit 3");
        m.out_state[2] = 0x80;
        CHECK(pmu_out_on(&m, 23) == 1, "O24 is byte 4 bit 7");
    }

    printf("\n passed %d   failed %d\n", g_pass, g_fail);
    printf(g_fail ? " DCU TESTS FAILED\n" : " ALL DCU TESTS PASSED\n");
    return g_fail ? 1 : 0;
}
