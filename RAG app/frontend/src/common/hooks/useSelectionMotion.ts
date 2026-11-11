import { useEffect } from 'react';

// Bridge pointer-selected documents with a cancellable fade while keeping keyboard navigation immediate.
export function useSelectionMotion(identity: string | undefined, selector: string) {
  useEffect(() => {
    if (
      !identity ||
      document.documentElement.dataset.inputModality !== 'pointer' ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    )
      return;
    const element = document.querySelector<HTMLElement>(selector);
    const animation = element?.animate([{ opacity: 0.72 }, { opacity: 1 }], {
      duration: 160,
      easing: 'cubic-bezier(0.23, 1, 0.32, 1)',
    });
    const cancel = () => animation?.cancel();
    document.addEventListener('keydown', cancel, { once: true, capture: true });
    return () => {
      animation?.cancel();
      document.removeEventListener('keydown', cancel, true);
    };
  }, [identity, selector]);
}
