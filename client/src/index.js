import React from 'react';
import ReactDOM from 'react-dom/client';
import { Client as Styletron } from 'styletron-engine-atomic';
import { Provider as StyletronProvider } from 'styletron-react';
import Routes from './routes';

const engine = new Styletron();


function App() {
  return (
    <React.StrictMode>
      <StyletronProvider value={engine}>
          <Routes />
      </StyletronProvider>
    </React.StrictMode>
  )
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <App />
);