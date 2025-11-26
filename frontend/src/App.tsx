import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import SetupWizard from './pages/SetupWizard';
import VerifyPage from './pages/VerifyPage';
import Dashboard from './pages/Dashboard';
import AdminAudit from './pages/AdminAudit';

const NavLink = ({ to, children }: { to: string; children: React.ReactNode }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${isActive
          ? 'bg-indigo-600 text-white shadow-md'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`}
    >
      {children}
    </Link>
  );
};

const NavBar = () => {
  return (
    <nav className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center gap-2">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span className="font-bold text-xl text-slate-800 tracking-tight">Auth<span className="text-indigo-600">Secure</span></span>
            </div>
            <div className="hidden sm:ml-10 sm:flex sm:space-x-4">
              <NavLink to="/">Verify</NavLink>
              <NavLink to="/setup">Setup</NavLink>
              <NavLink to="/dashboard">Dashboard</NavLink>
              <NavLink to="/admin">Admin</NavLink>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <div className="py-10 animate-fade-in">
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<VerifyPage />} />
                <Route path="/setup" element={<SetupWizard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/admin" element={<AdminAudit />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
