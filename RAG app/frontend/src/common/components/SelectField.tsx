import { useId, useLayoutEffect, useRef, useState } from 'react';
import { Check, ChevronDown } from 'lucide-react';
import { titleCaseLabel } from '../utils/format';

// Overlay options within the field width while preserving keyboard and focus support.
export function SelectField({
  label,
  value,
  options,
  disabled,
  suggested = false,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  disabled?: boolean;
  suggested?: boolean;
  onChange: (value: string) => void;
}) {
  const id = useId();
  const trigger = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [placement, setPlacement] = useState({ above: false, height: 280 });

  // Keep the floating list inside the viewport and open upward when space below is limited.
  useLayoutEffect(() => {
    if (!open) return;
    function positionOptions() {
      const bounds = trigger.current?.getBoundingClientRect();
      if (!bounds) return;
      const below = window.innerHeight - bounds.bottom - 16;
      const above = bounds.top - 16;
      const upward = below < 200 && above > below;
      setPlacement({ above: upward, height: Math.max(40, Math.min(280, upward ? above : below)) });
    }
    positionOptions();
    window.addEventListener('resize', positionOptions);
    window.addEventListener('scroll', positionOptions, true);
    return () => {
      window.removeEventListener('resize', positionOptions);
      window.removeEventListener('scroll', positionOptions, true);
    };
  }, [open]);

  // Move focus to an available option when opening from the keyboard.
  function openOptions(last = false) {
    setOpen(true);
    requestAnimationFrame(() => {
      const rows = list.current?.querySelectorAll<HTMLButtonElement>('[role="option"]');
      rows?.[last ? rows.length - 1 : 0]?.focus();
    });
  }

  return (
    <div
      data-next-selection={suggested || undefined}
      className={`field profile-field ${value ? 'is-selected' : ''} ${open ? 'select-open' : ''}`}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
      onKeyDown={(event) => {
        if (event.key === 'Escape' && open) {
          event.preventDefault();
          event.stopPropagation();
          setOpen(false);
          trigger.current?.focus();
        }
      }}
    >
      <span id={`${id}-label`}>{label}</span>
      <button
        ref={trigger}
        type="button"
        className="select-trigger"
        disabled={disabled}
        aria-labelledby={`${id}-label ${id}-value`}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? `${id}-options` : undefined}
        onClick={() => setOpen(!open)}
        onKeyDown={(event) => {
          if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            event.preventDefault();
            openOptions(event.key === 'ArrowUp');
          }
        }}
      >
        <span id={`${id}-value`}>{value ? titleCaseLabel(value) : `Select ${label}`}</span>
        <ChevronDown size={17} className={open ? 'select-chevron-open' : ''} aria-hidden="true" />
      </button>
      {open && !disabled && (
        <div
          ref={list}
          id={`${id}-options`}
          role="listbox"
          aria-labelledby={`${id}-label`}
          className={`select-options ${placement.above ? 'select-options-above' : ''}`}
          style={{ maxHeight: placement.height }}
          onKeyDown={(event) => {
            const rows = [
              ...event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="option"]'),
            ];
            const index = rows.indexOf(document.activeElement as HTMLButtonElement);
            let next = index;
            if (event.key === 'ArrowDown') next = (index + 1) % rows.length;
            else if (event.key === 'ArrowUp') next = (index - 1 + rows.length) % rows.length;
            else if (event.key === 'Home') next = 0;
            else if (event.key === 'End') next = rows.length - 1;
            else return;
            event.preventDefault();
            rows[next]?.focus();
          }}
        >
          {['', ...options].map((option) => (
            <button
              key={option}
              type="button"
              role="option"
              aria-selected={option === value}
              onClick={() => {
                onChange(option);
                setOpen(false);
                trigger.current?.focus();
              }}
            >
              <span>{option ? titleCaseLabel(option) : `Select ${label}`}</span>
              {option === value && <Check size={15} aria-hidden="true" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
