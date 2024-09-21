import { createRoot } from 'react-dom/client';

import { NavBar } from './navbar';

const domNode = document.getElementById('root');
const root = createRoot(domNode);

root.render(<NavBar />);
