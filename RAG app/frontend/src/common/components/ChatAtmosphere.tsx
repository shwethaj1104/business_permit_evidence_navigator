// Let a quiet chat backdrop settle once, without persistent movement or extra controls.
export function ChatAtmosphere() {
  return (
    <div className="chat-atmosphere" aria-hidden="true">
      {Array.from({ length: 6 }, (_, index) => (
        <span key={index}>
          <i />
        </span>
      ))}
    </div>
  );
}
