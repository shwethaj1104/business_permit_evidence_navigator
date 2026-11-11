// Show indeterminate activity only while a real request is in progress.
export function RequestActivity({ text }: { text: string }) {
  return (
    <span className="request-activity">
      <span className="request-activity-dots" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <span>{text}</span>
    </span>
  );
}
