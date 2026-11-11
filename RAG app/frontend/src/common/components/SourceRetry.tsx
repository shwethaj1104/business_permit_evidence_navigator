// Retry read-only collection requests without starting a capture or model call.
export function SourceRetry({ onRetry, busy }: { onRetry: () => void; busy: boolean }) {
  return (
    <div className="source-retry">
      <strong>Source collection unavailable</strong>
      <p>Retry loading the collection. This does not run a sync.</p>
      <button type="button" disabled={busy} onClick={onRetry}>
        {busy ? 'Loading sources…' : 'Retry sources'}
      </button>
    </div>
  );
}
