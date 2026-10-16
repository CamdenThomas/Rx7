/*
 * can_map.h — RX-7 FB vehicle CAN bus definitions
 *
 * Shared by the ICU and DCU. Both nodes include this file.
 * When it changes, BOTH firmware versions bump together.
 *
 * Bus: CAN2, 500 kbps, CAN 2.0B, 11-bit identifiers, little-endian.
 * Every message is 8 bytes. Byte 7 is a rolling counter.
 *
 * The map is data: 02-electrical/data/can_messages.csv and can_fields.csv
 * (rx7.py sql 02-PROJECTS/02-electrical "select * from can_fields"). If this
 * header and those rows disagree, the rows win and this file is bumped (F-012).
 *
 * WARNING: IDs 0x100-0x130 are the PMU's messages and their layout is fixed by
 * ECUMaster, not by us. Read the actual CAN export out of the PMU client and
 * reconcile before trusting these. [V-065]
 * IDs 0x200-0x400 are ours and are final.
 */

#ifndef CAN_MAP_H
#define CAN_MAP_H

#include <stdint.h>

#define CAN_BITRATE        500000
#define CAN_MSG_LEN        8
#define CAN_COUNTER_BYTE   7

/* ---------------- message identifiers ---------------- */

#define ID_PMU_STATE       0x100   /* 20 Hz */
#define ID_PMU_POWER       0x110   /* 10 Hz */
#define ID_PMU_OUTPUTS     0x120   /*  5 Hz */
#define ID_PMU_CHANNEL     0x130   /*  5 Hz, multiplexed */
#define ID_ICU_SENSORS     0x200   /* 20 Hz */
#define ID_ICU_HEALTH      0x210   /*  2 Hz */
#define ID_ICU_BODY        0x218   /*  2 Hz, fuel level - the ICU's since D-306 */
#define ID_ICU_BATT        0x220   /*  2 Hz, pack + cells 1-2 (D-345)          */
#define ID_ICU_CELLS       0x221   /*  2 Hz, cells 3-4 + spread (D-345)         */
#define ID_ICU_BATT_EXT    0x222   /*  NEVER SENT until W-330b: no source        */
#define ID_DCU_CLIMATE     0x300   /*  5 Hz */
#define ID_DCU_COMFORT     0x310   /*  2 Hz */
#define ID_DCU_RADAR       0x320   /* on change */
#define ID_PANEL_KEYS      0x400   /* on change + 2 Hz, sent by the DCU */

/* ---------------- timeouts, milliseconds ----------------
 * On timeout a receiver BLANKS the field. It never holds the last value.
 * A gauge frozen at its last reading is worse than one showing a fault. */

#define TMO_PMU_STATE      250
#define TMO_PMU_POWER      500
#define TMO_PMU_OUTPUTS   1000
#define TMO_ICU_SENSORS    250
#define TMO_DCU_CLIMATE   2000
#define TMO_DCU_COMFORT   2000
#define TMO_ICU_BODY      3000   /* the PMU logs a received-channel fault */
#define TMO_PANEL_KEYS    1000   /* on timeout every key reads released */
#define TMO_ICU_BATT      3000   /* 0x220 and 0x221 */

/* ---------------- enums ---------------- */

typedef enum { KEY_OFF = 0, KEY_ACC, KEY_RUN, KEY_START, KEY_FAULT } key_pos_t;   /* FAULT: the key ladder reads open, short or dead (R11) */
typedef enum { HL_OFF = 0, HL_PARK, HL_HEAD } headlight_pos_t;
typedef enum { TURN_OFF = 0, TURN_LEFT, TURN_RIGHT, TURN_HAZARD } turn_state_t;
typedef enum { POP_DOWN = 0, POP_RAISING, POP_UP, POP_LOWERING, POP_FAULT } popup_state_t;
typedef enum { CH_OFF = 0, CH_ON, CH_TRIPPED, CH_RETRYING } ch_status_t;
typedef enum { CLIM_OFF = 0, CLIM_VENT, CLIM_HEAT, CLIM_DEFROST, CLIM_AC } climate_mode_t;

/* wake source bits, 0x100 byte 1 - one bit per wake-strip input (can_fields 0x100/1, R11):
 * the strip cannot tell horn from hazard from a wink, they share input 4 */
#define WAKE_ACC           (1u << 0)   /* strip input 1 */
#define WAKE_RUN           (1u << 1)   /* strip input 2 */
#define WAKE_DOOR          (1u << 2)   /* strip input 3 */
#define WAKE_A8            (1u << 3)   /* strip input 4: horn / hazard / wink */
#define WAKE_SELF          (1u << 4)   /* strip input 5: the PMU's own O22 hold */
#define WAKE_BRAKE         (1u << 5)   /* strip input 6: the brake plunger (D-278) */
#define WAKE_DCU           (1u << 6)   /* strip input 7: the DCU's request (D-350) */
#define WAKE_HAZARD        WAKE_A8     /* older names for the same input */
#define WAKE_HORN          WAKE_A8
#define WAKE_LATCH         WAKE_SELF

/* input faults, 0x100 byte 6 (can_fields 0x100/6, R11): a ladder reading open, short or a
 * dead supply; A16's own fault is key_pos == KEY_FAULT */
#define INFAULT_A1         (1u << 0)
#define INFAULT_A2         (1u << 1)
#define INFAULT_A3         (1u << 2)
#define INFAULT_A4         (1u << 3)
#define INFAULT_A5         (1u << 4)
#define INFAULT_A6         (1u << 5)
#define INFAULT_A8         (1u << 6)
#define INFAULT_A15        (1u << 7)

/* global fault bits, 0x100 byte 2 */
#define FAULT_SOFTFUSE     (1u << 0)
#define FAULT_UNDERVOLT    (1u << 1)
#define FAULT_OVERVOLT     (1u << 2)
#define FAULT_OVERTEMP     (1u << 3)

/* sensor valid bits, 0x210 byte 0 */
#define SENS_RPM           (1u << 0)
#define SENS_WATER         (1u << 1)
#define SENS_OILTEMP       (1u << 2)
#define SENS_OILPRESS      (1u << 3)
#define SENS_VSS           (1u << 4)
#define SENS_FUEL          (1u << 5)

/* CAN health, 0x210 byte 2. b2 was 'keypad': the panel has no CAN node (D-355) */
#define CANH_PMU           (1u << 0)
#define CANH_DCU           (1u << 1)
#define CANH_AFR           (1u << 3)

/* tell-tales and warnings, 0x210 byte 3 (can_fields 0x210/3, Y10): what the ICU reads off
 * the wires - the charge lamp (IC05), the brake warning (IC06), the lamp tell-tales */
#define TT_CHARGE          (1u << 0)
#define TT_BRAKE           (1u << 1)
#define TT_TURN_L          (1u << 2)
#define TT_TURN_R          (1u << 3)
#define TT_HIGH_BEAM       (1u << 4)

/* radar band, 0x320 byte 1 (can_fields 0x320/1) */
#define BAND_X             (1u << 0)
#define BAND_K             (1u << 1)
#define BAND_KA            (1u << 2)
#define BAND_LASER         (1u << 3)

/* panel keys, 0x400 - bit n of `down` / `held` (F-016, F-018). Held = down
 * for >= 1 s. Bytes 0-1 down, 2-3 held (same bits), 4 the screen knob's
 * detent count, 5 the display level, 6 reserved, 7 counter (D-580).
 *
 * F-016 (D-380, the 3 x 3 matrix):   F-018 (D-492, the 4 x 3 matrix):
 *   b0  defog                          b0  rear-glass defog       ROW1 C1
 *   b1  hatch release                  b1  hatch release          ROW1 C2 (left plate)
 *   b2  fuel-door release              b2  fuel-door release      ROW1 C3 (left plate)
 *   b3  HVAC mode                      b3  fan mode (= HVAC mode) ROW2 C1
 *   b4  recirculate                    b4  recirculate            ROW2 C2
 *   b5  window DRV up                  b5  window DRV up contact  ROW2 C3
 *   b6  window DRV down                b6  window DRV down contact ROW3 C1
 *   b7  window PASS up                 b7  window PASS up contact ROW3 C2
 *   b8  window PASS down               b8  window PASS down contact ROW3 C3
 *   b9  mirror thumbstick press        b9  mirror stick press     (not matrix, ribbon 19)
 *   b10-15 reserved                    b10 mirror defog           ROW4 C1 (its own key, D-492)
 *                                      b11 spare                  ROW4 C2 (no key fitted)
 *                                      b12 spare                  ROW4 C3 (no key fitted)
 *                                      b13 centre knob push       (not matrix, ribbon 11)
 *                                      b14 screen knob push       (not matrix, I2C, D-580)
 *                                      b15 reserved
 * Append-only: every F-016 bit keeps its place, so a PMU rule or a log
 * decoder built on the old map reads the old keys unchanged. b0-b8 are
 * still the matrix row-major; ROW4 follows the stick press. The two
 * window contacts of one switch both down reads as neither (panel.h). */
#define PK_DEFOG           (1u << 0)
#define PK_HATCH           (1u << 1)
#define PK_FUEL_DOOR       (1u << 2)
#define PK_HVAC_MODE       (1u << 3)
#define PK_FAN_MODE        PK_HVAC_MODE   /* D-492's name for the same key */
#define PK_RECIRC          (1u << 4)
#define PK_WIN_DRV_UP      (1u << 5)
#define PK_WIN_DRV_DN      (1u << 6)
#define PK_WIN_PASS_UP     (1u << 7)
#define PK_WIN_PASS_DN     (1u << 8)
#define PK_MIRROR_PRESS    (1u << 9)
#define PK_MIRROR_DEFOG    (1u << 10)
#define PK_SPARE_R4C2      (1u << 11)
#define PK_SPARE_R4C3      (1u << 12)
#define PK_CENTRE_PUSH     (1u << 13)
#define PK_SCREEN_PUSH     (1u << 14)   /* the screen knob's push (SN32, D-580) */
#define PK_COUNT           15

/* battery freshness flags, 0x220 / 0x221 byte 6 - freshness, not health (D-345) */
#define BATT_ADV_FRESH     (1u << 0)   /* advertisement < 10 s old   */
#define BATT_GATT_CONN     (1u << 1)
#define BATT_CELLS_FRESH   (1u << 2)
#define BATT_CSUM_FAILED   (1u << 3)
#define BATT_RADIO_LOST    (1u << 4)   /* no line from the C3 for 3 s */

/* sensor fault type, 0x210 byte 1 */
#define SFAULT_OPEN        (1u << 0)
#define SFAULT_SHORT       (1u << 1)
#define SFAULT_RANGE       (1u << 2)
#define SFAULT_IMPLAUSIBLE (1u << 3)

/* ---------------- payloads ---------------- */

typedef struct __attribute__((packed)) {
    uint8_t key_pos;        /* key_pos_t                     */
    uint8_t wake_source;    /* WAKE_* bitfield               */
    uint8_t fault;          /* FAULT_* bitfield              */
    uint8_t headlight;      /* headlight_pos_t               */
    uint8_t turn;           /* turn_state_t                  */
    uint8_t popup;          /* popup_state_t                 */
    uint8_t input_fault;    /* INFAULT_* bitfield (R11)      */
    uint8_t counter;
} pmu_state_t;

typedef struct __attribute__((packed)) {
    uint16_t batt_mv;       /* millivolts                    */
    uint16_t total_ca;      /* 0.1 A units                   */
    uint8_t  charging;      /* 0 no, 1 yes                   */
    uint8_t  _rsv[2];
    uint8_t  counter;
} pmu_power_t;

typedef struct __attribute__((packed)) {
    uint8_t  _rsv[2];       /* was fuel_pct - moved to 0x218 */
    uint8_t  out_state[3];  /* 24 bits, one per O1..O24      */
    uint8_t  trip_index;    /* multiplexed channel 0..23     */
    uint8_t  trip_status;   /* ch_status_t for trip_index    */
    uint8_t  counter;
} pmu_outputs_t;

typedef struct __attribute__((packed)) {
    uint8_t  index;         /* 0..23 = O1..O24               */
    uint16_t current_ca;    /* 0.01 A                        */
    uint16_t limit_ca;      /* 0.01 A                        */
    uint8_t  status;        /* ch_status_t                   */
    uint8_t  _rsv;
    uint8_t  counter;
} pmu_channel_t;

/* ICU owns these sensors directly. If CAN2 fails entirely the ICU still
 * displays every field below from its own inputs. Only fuel level and
 * battery voltage degrade. See DECISIONS D-083. */
typedef struct __attribute__((packed)) {
    uint16_t rpm;           /* 1 rpm                         */
    int8_t   water_c;       /* degC, plain signed, no offset */
    int8_t   oil_temp_c;    /* degC, plain signed, no offset */
    uint16_t oil_press_cbar;/* 0.01 bar                      */
    uint8_t  speed_kph;
    uint8_t  counter;
} icu_sensors_t;

typedef struct __attribute__((packed)) {
    uint8_t sensor_valid;   /* SENS_* bitfield               */
    uint8_t sensor_fault;   /* SFAULT_* bitfield             */
    uint8_t can_health;     /* CANH_* bitfield               */
    uint8_t telltales;      /* TT_* bitfield (Y10)           */
    uint8_t _rsv[3];
    uint8_t counter;
} icu_health_t;

/* 0x218 - slow body data the ICU owns. Fuel level is read at the ICU from the
 * tank sender (electrical D-249); the PMU logs it, it never computes it. */
typedef struct __attribute__((packed)) {
    uint16_t fuel_pct;      /* 0.1 %                         */
    uint8_t  fuel_valid;    /* 0 fault, 1 valid              */
    uint8_t  _rsv[4];
    uint8_t  counter;
} icu_body_t;

/* 0x220 / 0x221 - the pack and its four cells, read by the ICU's ESP32-C3 from the
 * Ionic BMS over BLE (D-330, D-345). Voltages only: current, state of charge and
 * temperature have no source and are NOT published - not as 0, not as 0xFF. */
typedef struct __attribute__((packed)) {
    uint16_t pack_mv;       /* 1 mV, from the advertisement  */
    uint16_t cell1_mv;      /* 1 mV, from the type-01 frame  */
    uint16_t cell2_mv;
    uint8_t  flags;         /* BATT_* bitfield               */
    uint8_t  counter;
} icu_batt_t;

typedef struct __attribute__((packed)) {
    uint16_t cell3_mv;
    uint16_t cell4_mv;
    uint16_t spread_mv;     /* highest cell - lowest cell    */
    uint8_t  flags;         /* BATT_* bitfield, as 0x220     */
    uint8_t  counter;
} icu_cells_t;

typedef struct __attribute__((packed)) {
    uint8_t mode;           /* climate_mode_t                */
    uint8_t blower;         /* duty %, 0..100 (D-308)        */
    uint8_t target_c;
    int8_t  cabin_c;        /* degC, plain signed, no offset */
    uint8_t ac_request;     /* the A/C request to the ECU, which owns the clutch (engine D-489); 0 until the swap (D-211) */
    int8_t  outside_c;      /* degC; TEMP_INVALID until read */
    uint8_t dash_pct;       /* the dash-light level, % 0..100, 100 = full (SN31, D-577):
                             * the Display Unit dims to it while IC14 reads on */
    uint8_t counter;
} dcu_climate_t;

typedef struct __attribute__((packed)) {
    uint8_t  seat_heat;     /* b0-1 drv level, b2-3 pass     */
    uint8_t  seat_cool;     /* b0-1 drv, b2-3 pass           */
    uint8_t  mirror_heat;
    uint8_t  _rsv3;         /* was nozzle / de-icer (D-329)  */
    uint16_t bus_current_ca;/* 0.01 A                        */
    uint8_t  _rsv;
    uint8_t  counter;
} dcu_comfort_t;

typedef struct __attribute__((packed)) {
    uint8_t alert_level;    /* 0 none, 1..5                  */
    uint8_t band;           /* b0 X, b1 K, b2 Ka, b3 laser   */
    uint8_t direction;      /* 0 unknown, 1 front, 2 rear    */
    uint8_t _rsv[4];
    uint8_t counter;
} dcu_radar_t;

typedef struct __attribute__((packed)) {
    uint16_t down;          /* PK_* bitfield, little-endian  */
    uint16_t held;          /* PK_*, down for >= 1 s         */
    int8_t   screen_count;  /* the screen knob's detents on pages, rolling (D-580) */
    uint8_t  disp_pct;      /* the display level, % 10-100 (D-580) */
    uint8_t  _rsv;
    uint8_t  counter;
} panel_keys_t;

/* ---------------- helpers ---------------- */

/* Detect a stalled sender. Call on every receive; if the counter has not
 * advanced across the timeout window the sender is dead, not merely quiet. */
static inline uint8_t can_counter_advanced(uint8_t prev, uint8_t now)
{
    return (uint8_t)(now - prev) != 0u;
}

/* Channel index -> O-number, purely for display. Index 0 is O1. */
#define CH_INDEX_TO_OUTPUT(i)  ((i) + 1)

/* Temperature: stored as plain signed celsius in an int8_t.
 * Range -128..127 C covers every automotive temperature with room to spare,
 * so no offset is used. An offset would only add a class of bug. */
#define TEMP_ENCODE(c)   ((int8_t)(c))
#define TEMP_DECODE(b)   ((int)(int8_t)(b))

/* Sentinel for "no valid reading". Receivers must blank the field, not
 * display this value. */
#define TEMP_INVALID     ((int8_t)-128)

#endif /* CAN_MAP_H */
