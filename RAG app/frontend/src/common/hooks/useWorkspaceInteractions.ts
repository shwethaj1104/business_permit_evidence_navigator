import { useEffect } from 'react';

// Keep keyboard interactions immediate and return focus when an evidence disclosure closes.
export function useWorkspaceInteractions() {
  useEffect(() => {
    const root = document.documentElement;
    root.dataset.inputModality = 'keyboard';
    const pointer = () => {
      root.dataset.inputModality = 'pointer';
    };
    const keyboardModality = () => {
      root.dataset.inputModality = 'keyboard';
    };
    function keyboard(event: KeyboardEvent) {
      if (event.defaultPrevented || event.key !== 'Escape' || !(event.target instanceof Element))
        return;
      const disclosure = event.target.closest<HTMLDetailsElement>('.design-root details[open]');
      if (!disclosure) return;
      disclosure.open = false;
      disclosure.querySelector('summary')?.focus({ preventScroll: true });
      event.preventDefault();
    }
    document.addEventListener('pointerdown', pointer, true);
    document.addEventListener('keydown', keyboardModality, true);
    document.addEventListener('keydown', keyboard);
    return () => {
      document.removeEventListener('pointerdown', pointer, true);
      document.removeEventListener('keydown', keyboardModality, true);
      document.removeEventListener('keydown', keyboard);
      delete root.dataset.inputModality;
    };
  }, []);
}
