import { useId, useRef, useState } from 'react';
import { Check, ChevronDown } from 'lucide-react';

// Expand styled options in document flow with keyboard and focus support.
export function SelectField({
  label,
  value,
  options,
  disabled,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  disabled?: boolean;
  onChange: (value: string) => void;
}) {
  const id = useId();
  const trigger = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);

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
      className={`field profile-field ${value ? 'is-selected' : ''}`}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
      }}
      onKeyDown={(event) => {
        if (event.key === 'Escape') {
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
        <span id={`${id}-value`}>{value || `Select ${label.toLowerCase()}`}</span>
        <ChevronDown size={17} className={open ? 'select-chevron-open' : ''} aria-hidden="true" />
      </button>
      {open && !disabled && (
        <div
          ref={list}
          id={`${id}-options`}
          role="listbox"
          aria-labelledby={`${id}-label`}
          className="select-options"
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
              <span>{option || `Select ${label.toLowerCase()}`}</span>
              {option === value && <Check size={15} aria-hidden="true" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
