import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store';
import './styles/global.css';
import './styles/theme.css';
import './designs/common.css';
import { App } from './app/App';
import './designs/accessibility.css';
import './designs/motion.css';
import './designs/chat-refinements.css';
import './designs/executive/glass-polish.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>,
);
