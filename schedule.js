// ══════════════════════════════════════════════════
//  Schedule math — pure functions, no DOM, no globals.
//  Shared by index.html and schedule.test.mjs.
//  Every function takes what it needs so it can be tested directly.
// ══════════════════════════════════════════════════
const Schedule = (() => {

  // Local-time YYYY-MM-DD. Never use toISOString() here — that is UTC and
  // rolls the day over early for western timezones.
  function localDateKey(d) {
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }

  // Whole days elapsed from startDate to todayKey (both YYYY-MM-DD).
  // A start date in the future clamps to 0 rather than going negative.
  //
  // Counted through Date.UTC rather than by subtracting two local midnights:
  // a spring-forward puts only 23 hours in a day, so the millisecond
  // difference floors one day short and the whole schedule slips until the
  // autumn transition cancels it. UTC has no DST, so the count stays exact.
  function daysSinceStart(startDate, todayKey) {
    const utc = key => {
      const [y, m, d] = String(key).split('-').map(Number);
      return Date.UTC(y, m - 1, d);
    };
    const start = utc(startDate);
    const now = utc(todayKey);
    if (Number.isNaN(start) || Number.isNaN(now)) return 0;
    return Math.max(0, Math.round((now - start) / 86400000));
  }

  // 0-based index into the regular (non-thanksgiving) catechism list.
  function todaysCatechismIndex(settings, todayKey, regularCount) {
    const days   = daysSinceStart(settings.startDate, todayKey);
    const dpq    = Math.max(1, settings.daysPerCatechism);
    const startQ = Math.max(1, settings.startFromQ) - 1;
    const idx    = startQ + Math.floor(days / dpq);
    return Math.min(idx, regularCount - 1);
  }

  // 1-based day within the current catechism's cycle.
  function dayOfCycle(settings, todayKey) {
    const days = daysSinceStart(settings.startDate, todayKey);
    const dpq  = Math.max(1, settings.daysPerCatechism);
    return (days % dpq) + 1;
  }

  // Days from today until the catechism at `index` becomes the current one.
  // Subtracts the part of the current cycle already served — without that
  // term, on the last day of a cycle the next card reads as a full cycle
  // away when it actually arrives tomorrow.
  function daysUntilIndex(settings, todayKey, index, todayIdx) {
    const dpq = Math.max(1, settings.daysPerCatechism);
    return (index - todayIdx) * dpq - (dayOfCycle(settings, todayKey) - 1);
  }

  // Days from today until the whole list is finished.
  function daysUntilComplete(settings, todayKey, regularCount, todayIdx) {
    const dpq = Math.max(1, settings.daysPerCatechism);
    return (regularCount - todayIdx) * dpq - (dayOfCycle(settings, todayKey) - 1);
  }

  return {
    localDateKey, daysSinceStart, todaysCatechismIndex,
    dayOfCycle, daysUntilIndex, daysUntilComplete
  };
})();

globalThis.Schedule = Schedule;
