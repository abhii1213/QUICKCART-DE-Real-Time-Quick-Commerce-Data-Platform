export const buildEvent = (eventType, sourceSystem, payload) => {
  return {
    event_id: crypto.randomUUID(),
    event_type: eventType,
    event_version: "1.0",
    event_ts: new Date().toISOString(),
    source_system: sourceSystem,
    payload,
  };
};