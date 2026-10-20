import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Layout from './components/Layout';
import InvoiceForm from './components/InvoiceForm';
import AdminDashboard from './components/AdminDashboard';

function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <p className="text-gray-500 animate-pulse">Verifying session...</p>
      </div>
    );
  }

  const token = localStorage.getItem('token');
  
  if (!user && !token) {
    return <Navigate to="/login" replace />;
  }

  if (!user && token) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading profile...</p>
      </div>
    );
  }

  if (requireAdmin && user.role !== 'admin') {
    return <Navigate to="/entry" replace />;
  }

  return <Layout>{children}</Layout>;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
     return <div className="h-screen bg-gray-50"></div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route 
        path="/" 
        element={
          !user ? <Navigate to="/login" replace /> : 
          user.role === 'admin' ? <Navigate to="/dashboard" replace /> : 
          <Navigate to="/entry" replace />
        } 
      />

      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute requireAdmin={true}>
            <AdminDashboard />
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/entry" 
        element={
          <ProtectedRoute>
            <InvoiceForm />
          </ProtectedRoute>
        } 
      />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}