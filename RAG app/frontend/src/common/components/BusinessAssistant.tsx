import { useId } from 'react';

// Draw a warm professional greeting character with a small, reduced-motion-aware wave.
export function BusinessAssistant() {
  const id = useId();
  return (
    <div className="business-assistant" aria-hidden="true">
      <div className="assistant-halo" />
      <svg viewBox="0 0 240 240" fill="none" className="assistant-portrait">
        <defs>
          <linearGradient
            id={`${id}-hair`}
            x1="74"
            y1="42"
            x2="164"
            y2="162"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#614C41" />
            <stop offset="1" stopColor="#302D2B" />
          </linearGradient>
          <linearGradient
            id={`${id}-skin`}
            x1="99"
            y1="72"
            x2="144"
            y2="147"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#F2C6A6" />
            <stop offset="1" stopColor="#D9A283" />
          </linearGradient>
          <linearGradient
            id={`${id}-jacket`}
            x1="66"
            y1="162"
            x2="162"
            y2="221"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#386458" />
            <stop offset="1" stopColor="#193D35" />
          </linearGradient>
          <radialGradient id={`${id}-back`} cx=".45" cy=".35" r=".75">
            <stop stopColor="#F8FAEE" />
            <stop offset="1" stopColor="#E3EDD4" />
          </radialGradient>
        </defs>
        <circle cx="120" cy="120" r="106" fill={`url(#${id}-back)`} />
        <circle cx="120" cy="120" r="96" stroke="#D0DFBE" strokeDasharray="2 8" />
        <ellipse cx="120" cy="214" rx="63" ry="9" fill="#CDDDC0" opacity=".6" />
        <path
          d="M72 93c-3-34 15-57 47-57 35 0 53 24 49 62l-7 61c-29 12-60 10-84-2l-5-64Z"
          fill={`url(#${id}-hair)`}
        />
        <path d="M57 216c2-34 21-59 49-63h28c30 5 49 28 52 63H57Z" fill={`url(#${id}-jacket)`} />
        <path d="M107 139h26v23l-13 22-13-22v-23Z" fill="#D69D7D" />
        <path d="m102 157 18 27 19-27-6 54h-27l-4-54Z" fill="#FFFDF4" />
        <path
          d="m100 154-12 18 17 11-9 10 24 23M140 154l12 18-17 11 9 10-24 23"
          stroke="#6D8F7A"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <ellipse cx="86" cy="109" rx="6" ry="10" fill="#DCA787" />
        <ellipse cx="155" cy="109" rx="6" ry="10" fill="#DCA787" />
        <path
          d="M87 90c0-24 13-38 33-38s34 14 34 38v25c0 23-16 43-34 43s-33-20-33-43V90Z"
          fill={`url(#${id}-skin)`}
        />
        <path
          d="M78 96c-5-37 17-57 42-57 32 0 48 27 42 58-17-5-27-17-32-32-9 17-25 28-52 31Z"
          fill={`url(#${id}-hair)`}
        />
        <path
          d="M91 73c8-17 24-24 39-23"
          stroke="#8D7460"
          strokeWidth="3"
          strokeLinecap="round"
          opacity=".45"
        />
        <path
          d="M95 104c5-3 10-3 14-1M132 103c4-2 9-2 13 1"
          stroke="#765345"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M96 114c3-5 10-5 13 0M132 114c3-5 9-5 12 0"
          stroke="#473A33"
          strokeWidth="2.7"
          strokeLinecap="round"
        />
        <ellipse cx="99" cy="125" rx="7" ry="4" fill="#D88678" opacity=".27" />
        <ellipse cx="141" cy="125" rx="7" ry="4" fill="#D88678" opacity=".27" />
        <path d="m120 116-3 12 5 1" stroke="#C08970" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M108 136q12 14 25-1c-7 2-17 3-25 1Z" fill="#AF6C5E" />
        <path d="M111 136c6 1 12 1 18 0" stroke="#FFF7E8" strokeWidth="2.8" strokeLinecap="round" />
        <path
          d="M84 118c-8 8-2 16 3 10M157 118c7 8 2 16-3 10"
          stroke="#CCA65B"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
        <path d="M112 165c5 7 12 7 17 0" stroke="#C9AC70" strokeWidth="1.8" />
        <circle cx="120" cy="174" r="2.2" fill="#C9AC70" />
        <g className="assistant-wave">
          <path d="m165 200 12-43 19 5-8 44-23-6Z" fill={`url(#${id}-jacket)`} />
          <path
            d="m179 162-5-17c-3-7-5-13-2-15 3-1 5 5 7 8l-2-22c0-4 4-4 5 0l4 18-1-27c0-4 4-4 5 0l3 26 2-23c0-4 4-3 4 1l-1 24 5-16c1-3 5-2 4 2l-6 27c-2 9-8 16-14 17l-8-3Z"
            fill={`url(#${id}-skin)`}
          />
          <path d="m178 161 15 4" stroke="#F8FAEE" strokeWidth="4" />
        </g>
        <path d="m46 80 3-8 3 8 8 3-8 3-3 8-3-8-8-3 8-3Z" fill="#9CB776" />
        <circle cx="189" cy="62" r="4" fill="#B5C98E" />
        <circle cx="57" cy="152" r="3" fill="#C9D8AD" />
      </svg>
      <span className="assistant-welcome-badge">
        A friendly start <span>✦</span>
      </span>
    </div>
  );
}
