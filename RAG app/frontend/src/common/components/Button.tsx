import type { ButtonHTMLAttributes } from 'react';

// Keep button styles and disabled behavior consistent across both tabs.
export function Button({ className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`button ${className}`} {...props} />;
}
