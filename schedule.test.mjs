// Unit tests for the schedule math in schedule.js.
//
//     node --test
//
// Zero dependencies. schedule.js is a classic script (index.html loads it with
// a plain <script> tag), so it is evaluated in a vm context rather than
// imported — that keeps the browser side free of module plumbing.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const ctx = vm.createContext({});
vm.runInContext(readFileSync(new URL('./schedule.js', import.meta.url), 'utf8'), ctx);
const S = ctx.Schedule;

const REGULAR = 91;                       // non-thanksgiving cards
const settings = (o = {}) => ({ startDate: '2026-01-01', daysPerCatechism: 3, startFromQ: 1, ...o });

test('localDateKey uses local time, not UTC', () => {
  // 23:30 local on the 5th must be the 5th. toISOString() would say the 6th
  // for any timezone west of UTC — the bug the previous commit set out to fix.
  assert.equal(S.localDateKey(new Date(2026, 0, 5, 23, 30)), '2026-01-05');
  assert.equal(S.localDateKey(new Date(2026, 0, 5, 0, 1)), '2026-01-05');
  assert.equal(S.localDateKey(new Date(2026, 10, 9)), '2026-11-09');   // zero-padding
});

test('daysSinceStart counts whole local days', () => {
  assert.equal(S.daysSinceStart('2026-01-01', '2026-01-01'), 0);
  assert.equal(S.daysSinceStart('2026-01-01', '2026-01-02'), 1);
  assert.equal(S.daysSinceStart('2026-01-01', '2026-02-01'), 31);
});

test('daysSinceStart clamps a future start date to zero', () => {
  // Setting a start date in the future must not produce a negative index.
  assert.equal(S.daysSinceStart('2026-06-01', '2026-01-01'), 0);
});

test('daysSinceStart is unaffected by a DST transition', () => {
  // US DST begins 2026-03-08. A naive UTC-millisecond diff would floor to 20.
  assert.equal(S.daysSinceStart('2026-03-01', '2026-03-21'), 20);
});

test('dayOfCycle runs 1..daysPerCatechism and wraps', () => {
  const s = settings({ daysPerCatechism: 3 });
  assert.equal(S.dayOfCycle(s, '2026-01-01'), 1);
  assert.equal(S.dayOfCycle(s, '2026-01-02'), 2);
  assert.equal(S.dayOfCycle(s, '2026-01-03'), 3);
  assert.equal(S.dayOfCycle(s, '2026-01-04'), 1);   // next card
});

test('dayOfCycle is always 1 when a card lasts one day', () => {
  const s = settings({ daysPerCatechism: 1 });
  for (const d of ['2026-01-01', '2026-01-02', '2026-01-09']) {
    assert.equal(S.dayOfCycle(s, d), 1);
  }
});

test('todaysCatechismIndex advances once per cycle', () => {
  const s = settings({ daysPerCatechism: 3 });
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR), 0);
  assert.equal(S.todaysCatechismIndex(s, '2026-01-03', REGULAR), 0);   // last day of cycle
  assert.equal(S.todaysCatechismIndex(s, '2026-01-04', REGULAR), 1);   // rollover
  assert.equal(S.todaysCatechismIndex(s, '2026-01-07', REGULAR), 2);
});

test('startFromQ offsets the starting card', () => {
  const s = settings({ daysPerCatechism: 3, startFromQ: 50 });
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR), 49);   // 0-indexed
  assert.equal(S.todaysCatechismIndex(s, '2026-01-04', REGULAR), 50);
});

test('an explicit startOrdinal overrides the startFromQ position', () => {
  const s = settings({ daysPerCatechism: 3, startFromQ: 1 });
  // Callers that address by number resolve the ordinal themselves.
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR, 49), 49);
  assert.equal(S.todaysCatechismIndex(s, '2026-01-04', REGULAR, 49), 50);
});

test('startOrdinal 0 is honoured, not treated as absent', () => {
  // A falsy-but-valid ordinal must not fall through to the startFromQ path.
  const s = settings({ daysPerCatechism: 3, startFromQ: 50 });
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR, 0), 0);
});

test('a bad startOrdinal falls back to the startFromQ position', () => {
  const s = settings({ daysPerCatechism: 3, startFromQ: 10 });
  for (const bad of [undefined, null, -1, 1.5, NaN, 'x']) {
    assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR, bad), 9,
                 `startOrdinal ${String(bad)} should fall back`);
  }
});

test('a gap in the numbering does not shift the schedule', () => {
  // Numbers 1,2,4,5 -> catechism 4 sits at ordinal 2. Resolving by number
  // keeps the start correct where a 1-based position would be off by one.
  const numbers = [1, 2, 4, 5];
  const ordinalOf = n => numbers.indexOf(n);
  const s = settings({ daysPerCatechism: 1, startFromQ: 4 });

  assert.equal(ordinalOf(4), 2);
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', numbers.length, ordinalOf(4)), 2);
  assert.equal(numbers[S.todaysCatechismIndex(s, '2026-01-02', numbers.length, ordinalOf(4))], 5);
  // The old positional reading would have started at index 3 — catechism 5.
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', numbers.length), 3);
});

test('todaysCatechismIndex clamps at the end of the list', () => {
  const s = settings({ daysPerCatechism: 1, startDate: '2020-01-01' });
  assert.equal(S.todaysCatechismIndex(s, '2026-01-01', REGULAR), REGULAR - 1);
});

test('a nonsensical daysPerCatechism does not divide by zero', () => {
  for (const dpq of [0, -5]) {
    const s = settings({ daysPerCatechism: dpq });
    assert.equal(S.dayOfCycle(s, '2026-01-02'), 1);
    assert.ok(Number.isInteger(S.todaysCatechismIndex(s, '2026-01-02', REGULAR)));
  }
});

test('daysUntilIndex accounts for the current partial cycle', () => {
  const s = settings({ daysPerCatechism: 3 });

  // On day 1 of 3, the next card is a full cycle away.
  assert.equal(S.daysUntilIndex(s, '2026-01-01', 1, 0), 3);
  // On day 2 it is two days out...
  assert.equal(S.daysUntilIndex(s, '2026-01-02', 1, 0), 2);
  // ...and on the last day of the cycle it arrives TOMORROW. The old formula,
  // (i - todayIdx) * dpq, said 3 here — two days wrong, and every later row
  // inherited the same shift.
  assert.equal(S.daysUntilIndex(s, '2026-01-03', 1, 0), 1);

  assert.equal(S.daysUntilIndex(s, '2026-01-03', 2, 0), 4);
});

test('daysUntilIndex is zero for the current card', () => {
  const s = settings({ daysPerCatechism: 3 });
  assert.equal(S.daysUntilIndex(s, '2026-01-01', 0, 0), 0);
});

test('daysUntilComplete counts the remaining cards, less days already served', () => {
  const s = settings({ daysPerCatechism: 3 });

  // Sitting on the last card, day 1 of 3: three days to go.
  assert.equal(S.daysUntilComplete(s, '2026-01-01', REGULAR, REGULAR - 1), 3);
  // Same card, day 3 of 3: finished tomorrow.
  assert.equal(S.daysUntilComplete(s, '2026-01-03', REGULAR, REGULAR - 1), 1);

  // From the very first card: 91 cards x 3 days, minus the day already served.
  assert.equal(S.daysUntilComplete(s, '2026-01-01', REGULAR, 0), REGULAR * 3);
  assert.equal(S.daysUntilComplete(s, '2026-01-02', REGULAR, 0), REGULAR * 3 - 1);
});

test('one-day cycles need no partial-cycle adjustment', () => {
  const s = settings({ daysPerCatechism: 1 });
  assert.equal(S.daysUntilIndex(s, '2026-01-01', 1, 0), 1);
  assert.equal(S.daysUntilIndex(s, '2026-01-05', 3, 0), 3);
});
