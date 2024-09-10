import { useCallback } from 'react';

const useEventTracker = (storageKey = "FrontendActivity") => {
  const logEvent = useCallback((eventDetails) => {
    let events = JSON.parse(localStorage.getItem(storageKey)) || {};

    if (events[eventDetails.id]) {
      events[eventDetails.id].time = new Date().toISOString();
      events[eventDetails.id].count += 1;
    } else {
      events[eventDetails.id] = {
        type: eventDetails.type,
        details: eventDetails.details,
        time: new Date().toISOString(),
        count: 1,
      };
    }

    localStorage.setItem(storageKey, JSON.stringify(events));
  }, [storageKey]);

  const getEvents = useCallback(() => {
    return JSON.parse(localStorage.getItem(storageKey)) || {};
  }, [storageKey]);

  const reset = useCallback(() => {
    localStorage.removeItem(storageKey);
  }, [storageKey]);

  return { reset, logEvent, getEvents };
};

export default useEventTracker;