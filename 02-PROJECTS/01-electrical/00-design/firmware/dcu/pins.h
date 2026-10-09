/*
 * pins.h — the DCU carrier's pin map: Teensy 4.1 edge pins and the
 * TCA9539-Q1 expander's ports (H-002, D-452)
 *
 * Owns (R6), from 02-PROJECTS/01-electrical/data:
 *   dcu_channels.teensy_pin   every number below, channel by channel
 *   panel_ribbon              which ribbon conductor each panel pin reads
 * The sheet (cad/dcu-carrier, checked against the same rows by cad/check.py)
 * is drawn from the same column, so a pin moved in the record moves here.
 *
 * No Arduino headers: tests/test_dcu.cpp includes this file and checks the
 * map (every edge pin 0-41 used once, nothing on the bottom pads 48-54, the
 * fan encoder on 40 / 41, I2C on 18 / 19). Analog inputs are given by pin
 * number (14 = A0), which Teensy's analogRead() takes as it is.
 */

#ifndef DCU_PINS_H
#define DCU_PINS_H

#include <stdint.h>

/* ------------------------- Teensy edge pins ------------------------- */
/* SN26: CAN2 is 0 CRX2 / 1 CTX2, ACAN_T4's can2 default - not set here.  */
#define PIN_CAN_RX          0
#define PIN_CAN_TX          1
static const int PIN_SERVO[3]   = { 2, 3, 4 };       /* SN15 mode · blend · recirc (climate.h order) */
static const int PIN_COMFORT[5] = { 5, 6, 7, 8, 9 }; /* SN16 seat heat DRV · PASS, seat cool DRV · PASS
                                                      * (BTS3011TE low side) · mirror heat IN (BTT6050) */
static const int PIN_BLOWER      = 10;               /* SN14, PWM 25 kHz, own timer */
static const int PIN_WAKE        = 11;               /* SN21, NPN into a 12 V PMOS -> DP-DCU 6 */
static const int PIN_EXP_INT     = 12;               /* SN17, TCA9539 INT, open drain, pulled up */
static const int PIN_EXP_RESET   = 13;               /* SN17, TCA9539 RESET, active low, pulled down
                                                      * (also the Teensy's LED: it lights while released) */
static const int PIN_CABIN_NTC   = 14;               /* SN11, A0 */
static const int PIN_OAT_NTC     = 15;               /* SN12, A1 */
static const int PIN_CURRENT     = 16;               /* SN13, A2 */
static const int PIN_JOY_PRESS   = 17;               /* SN18, ribbon 19 */
static const int PIN_I2C_SDA     = 18;               /* Wire, to the TCA9539 (D-452) */
static const int PIN_I2C_SCL     = 19;
static const int PIN_JOY_X       = 20;               /* SN18, A6, ribbon 17 */
static const int PIN_JOY_Y       = 21;               /* SN18, A7, ribbon 18 */
static const int PIN_WIN[4]      = { 22, 23, 24, 25 }; /* SN22 BTT6200 IN0-3: DRV up, DRV down, PASS up,
                                                        * PASS down -> DP-DCU-B 1-4 */
static const int PIN_REL_HATCH   = 26;               /* SN23, K3 85 via DP-DCU-B 10 */
static const int PIN_REL_FUEL    = 27;               /* SN23, K4 85 via DP-DCU-B 11 */
static const int PIN_ROW[3]      = { 28, 29, 30 };   /* SN19, ribbon 3-5 */
static const int PIN_COL[3]      = { 31, 32, 33 };   /* SN19, ribbon 6-8 */
enum { ENC_FAN = 0, ENC_TEMP, ENC_SEAT_DRV, ENC_SEAT_PASS, ENC_COUNT };
static const int PIN_ENC_A[ENC_COUNT] = { 40, 34, 36, 38 };   /* SN20, ribbon 9, 11, 13, 15 */
static const int PIN_ENC_B[ENC_COUNT] = { 41, 35, 37, 39 };   /* SN20, ribbon 10, 12, 14, 16 -
                                                               * the fan moved off 18 / 19 (D-452) */

/* ------------------------- TCA9539-Q1 ports (U12) -------------------------
 * Bit n of the 16-bit word is port P0n for n < 8 and P1(n-8) above. The
 * order is dcu_channels': SN17 "P00-P05 IN1/EN1-IN3/EN3, P06 EN4, P07
 * nSLEEP, P10 nFAULT", SN22 "DEN, DSEL0, DSEL1 on P11-P13", SN16 "mirror heat
 * DEN on P14", SN26 "STB on P15", SN24 "power-good on P16". DRV8962 channel
 * 1 is the motor common, 2 the left motor, 3 the right, 4 the clutch sink
 * (D-360; the sheet's OUT1-4 to DP-DCU-B 5-8).                           */
#define EXP_P(port, bit)   ((uint16_t)(1u << ((port) * 8 + (bit))))
#define EXP_MIR_IN1        EXP_P(0, 0)   /* common  - high or low   */
#define EXP_MIR_EN1        EXP_P(0, 1)   /*           off = open    */
#define EXP_MIR_IN2        EXP_P(0, 2)   /* left    */
#define EXP_MIR_EN2        EXP_P(0, 3)
#define EXP_MIR_IN3        EXP_P(0, 4)   /* right   */
#define EXP_MIR_EN3        EXP_P(0, 5)
#define EXP_MIR_EN4        EXP_P(0, 6)   /* clutch: IN4 tied low, EN4 on = low FET sinks the coils */
#define EXP_MIR_NSLEEP     EXP_P(0, 7)   /* low = asleep; R35 holds it low through a reset */
#define EXP_MIR_NFAULT     EXP_P(1, 0)   /* input, low = fault (R36 pull-up) */
#define EXP_WIN_DEN        EXP_P(1, 1)   /* BTT6200 diagnosis enable - IS is unread (D-452) */
#define EXP_WIN_DSEL0      EXP_P(1, 2)
#define EXP_WIN_DSEL1      EXP_P(1, 3)
#define EXP_MH_DEN         EXP_P(1, 4)   /* BTT6050 diagnosis enable - IS unread */
#define EXP_CAN_STB        EXP_P(1, 5)   /* TCAN1042 STB: low = normal; R8 holds it low through a reset */
#define EXP_PG_5V          EXP_P(1, 6)   /* input, the logic buck's power-good */
#define EXP_P17            EXP_P(1, 7)   /* input. D-452 calls it spare; the sheet wires the four
                                          * BTS3011TE STATUS pins to it (SEAT_STATUS) - read, not
                                          * acted on, until the record names it (confirm) */

#define EXP_INPUTS   ((uint16_t)(EXP_MIR_NFAULT | EXP_PG_5V | EXP_P17))
#define EXP_OUTPUTS  ((uint16_t)~EXP_INPUTS)

#endif /* DCU_PINS_H */
