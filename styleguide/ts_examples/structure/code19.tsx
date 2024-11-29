import { createDomain, guard, sample } from "effector";
import { AnalyticsEvent } from "./types";
import { initializeAnalytics, sendEvent } from "./lib";

const analyticsDomain = createDomain();

const sendDataToAnalytics = analyticsDomain.createEvent<AnalyticsEvent>();
const sendEventToQueue = analyticsDomain.createEvent<AnalyticsEvent>();
const delayedEventsSent = analyticsDomain.createEvent();

const initializeAnalyticsFx = analyticsDomain.createEffect({
  handler: initializeAnalytics,
  sid: "INIT analytics",
});
const sendEventFx = analyticsDomain.createEffect({
  handler: sendEvent,
  sid: "SEND analytics",
});
const sendManyEventsFx = analyticsDomain.createEffect({
  handler: (events: AnalyticsEvent[]) => Promise.all(events.map(sendEventFx)),
});

const $initialized = analyticsDomain
  .createStore(false)
  .on(initializeAnalyticsFx.done, () => true);

const $notInitialized = $initialized.map((initialized) => !initialized);

const $delayedEvents = analyticsDomain
  .createStore<AnalyticsEvent[]>([])
  .on(sendEventToQueue, (events, newEvent) => [...events, newEvent])
  .reset(delayedEventsSent);

guard({
  source: sendDataToAnalytics,
  target: sendEventFx,
  filter: $initialized,
});
guard({
  source: sendDataToAnalytics,
  target: sendEventToQueue,
  filter: $notInitialized,
});

sample({
  source: $delayedEvents,
  target: [sendManyEventsFx, delayedEventsSent],
  clock: initializeAnalyticsFx.done,
});

export {
  analyticsDomain,
  sendDataToAnalytics,
  initializeAnalyticsFx,
  sendEventFx,
};
