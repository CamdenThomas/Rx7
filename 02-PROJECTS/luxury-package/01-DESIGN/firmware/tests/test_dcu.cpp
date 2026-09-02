/*
 * test_dcu.cpp — desktop verification of the DCU logic (F-001)
 *
 * Compiles the REAL climate.h + can_map.h from ../dcu. Covers the seat
 * interlock (D-073), comfort gating, keypad edges, servo mapping, and
 * the SD climate-memory CRC.
 *
 * Build (w64devkit on PATH):
 *   g++ test_dcu.cpp -o test_dcu.exe -std=c++17 -O2 -I../dcu && test_dcu
 */
#include <cstdio>
#include <cstring>
#include "climate.h"

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

    printf("\n passed %d   failed %d\n", g_pass, g_fail);
    printf(g_fail ? " DCU TESTS FAILED\n" : " ALL DCU TESTS PASSED\n");
    return g_fail ? 1 : 0;
}
