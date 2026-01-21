import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { appLogger } from '../utils/logger';
import {
  User,
  Lock,
  Eye,
  EyeOff,
  Box
} from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(identifier, password);
      // Small delay to ensure state is updated before navigation
      await new Promise(resolve => setTimeout(resolve, 100));
      navigate(from, { replace: true });
    } catch (err: any) {
      const errorMessage = err.message || 'Invalid credentials';
      setError(errorMessage);
      appLogger.error('Login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="foundry-modern-login">
      <style>{`
        .foundry-modern-login {
          display: flex;
          height: 100vh;
          width: 100vw;
          background: #030303;
          font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
          overflow: hidden;
        }

        /* LEFT SIDE - BRAND VISUAL */
        .visual-panel {
          flex: 1.1;
          background: linear-gradient(135deg, #f97316 0%, #9a3412 100%);
          position: relative;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 0 8%;
          color: white;
          overflow: hidden;
          z-index: 1;
        }

        .welcome-content {
          position: relative;
          z-index: 10;
          max-width: 500px;
          animation: fade-in-up 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
          opacity: 0;
        }

        .welcome-content h1 {
          font-size: 4rem;
          font-weight: 800;
          margin-bottom: 1.5rem;
          letter-spacing: -0.04em;
          line-height: 1.1;
        }

        .welcome-content p {
          font-size: 1.25rem;
          line-height: 1.6;
          opacity: 0.9;
          font-weight: 400;
          color: #fff;
        }

        /* SLANTED PILL SHAPES */
        .shape {
          position: absolute;
          border-radius: 99px;
          transform: rotate(-35deg);
          z-index: 2;
          filter: blur(0.5px);
          opacity: 0;
          animation: shape-reveal 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        @keyframes shape-reveal {
          from { opacity: 0; transform: rotate(-35deg) translateY(50px); }
          to { opacity: 1; transform: rotate(-35deg) translateY(0); }
        }

        .shape-1 {
          width: 320px;
          height: 90px;
          background: linear-gradient(to right, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
          bottom: 12%;
          left: -40px;
          animation: shape-reveal 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards, float-slow 8s infinite ease-in-out 1.2s;
        }

        .shape-2 {
          width: 260px;
          height: 70px;
          background: linear-gradient(to right, rgba(0,0,0,0.1), transparent);
          bottom: 4%;
          left: 140px;
          animation: shape-reveal 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards, float-slow 10s infinite ease-in-out reverse 1.5s;
        }

        .shape-3 {
          width: 190px;
          height: 45px;
          background: rgba(255,255,255,0.15);
          bottom: 22%;
          left: 60px;
          animation: shape-reveal 1.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards, float-slow 12s infinite ease-in-out 1.8s;
        }

        .shape-4 {
          width: 450px;
          height: 110px;
          background: linear-gradient(to right, rgba(255,255,255,0.1), transparent);
          bottom: -40px;
          left: 280px;
          animation: shape-reveal 2.1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        @keyframes float-slow {
          0%, 100% { transform: rotate(-35deg) translate(0, 0); }
          50% { transform: rotate(-35deg) translate(20px, -20px); }
        }

        .glow-orb {
          position: absolute;
          width: 400px;
          height: 400px;
          background: #f97316;
          border-radius: 50%;
          filter: blur(150px);
          top: 10%;
          right: -150px;
          opacity: 0;
          animation: orb-glow 3s ease-in-out forwards;
        }

        @keyframes orb-glow {
          from { opacity: 0; transform: scale(0.8); }
          to { opacity: 0.3; transform: scale(1); }
        }

        /* RIGHT SIDE - LOGIN FORM */
        .form-panel {
          flex: 0.9;
          background: #030303;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 4rem;
          z-index: 10;
          border-left: 1px solid #161616;
          position: relative;
        }

        .login-card {
          width: 100%;
          max-width: 400px;
          text-align: center;
        }

        .animate-in {
          animation: fade-in-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
          opacity: 0;
        }

        .delay-1 { animation-delay: 0.1s; }
        .delay-2 { animation-delay: 0.2s; }
        .delay-3 { animation-delay: 0.3s; }
        .delay-4 { animation-delay: 0.4s; }
        .delay-5 { animation-delay: 0.5s; }

        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .logo-mark {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 56px;
          height: 56px;
          background: #f97316;
          border-radius: 16px;
          margin-bottom: 2rem;
          box-shadow: 0 10px 20px rgba(249, 115, 22, 0.2);
          transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .logo-mark:hover {
          transform: scale(1.1) rotate(5deg);
        }

        .login-card h2 {
          color: #f97316;
          font-weight: 800;
          font-size: 1.25rem;
          margin-bottom: 2.5rem;
          letter-spacing: 0.2em;
          text-transform: uppercase;
        }

        .input-group {
          margin-bottom: 1.25rem;
          position: relative;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .input-wrapper input {
          width: 100%;
          background: #09090b;
          border: 1px solid #18181b;
          padding: 1rem 1.25rem 1rem 3.75rem;
          border-radius: 99px;
          font-size: 1rem;
          color: #fff;
          outline: none;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .input-wrapper input:focus {
          border-color: #f97316;
          background: #0d0d10;
          box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.1);
          transform: translateY(-2px);
        }

        .input-icon {
          position: absolute;
          left: 1.5rem;
          color: #f97316;
          opacity: 0.9;
          transition: transform 0.3s;
        }

        .input-wrapper input:focus + .input-icon {
          transform: scale(1.1);
        }

        .eye-icon {
          position: absolute;
          right: 1.5rem;
          color: #3f3f46;
          cursor: pointer;
          border: none;
          background: none;
          display: flex;
          align-items: center;
          transition: all 0.2s;
          padding: 0;
        }

        .eye-icon:hover {
          color: #f97316;
          transform: scale(1.1);
        }

        .form-options {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin: 1.5rem 1rem;
          font-size: 0.875rem;
          color: #71717a;
          font-weight: 500;
        }

        .remember-me {
          display: flex;
          align-items: center;
          gap: 0.625rem;
          cursor: pointer;
          transition: color 0.2s;
        }

        .remember-me:hover {
          color: #a1a1aa;
        }

        .remember-me input {
          width: 1rem;
          height: 1rem;
          accent-color: #f97316;
          cursor: pointer;
        }

        .forgot-password {
          color: #71717a;
          text-decoration: none;
          transition: all 0.2s;
        }

        .forgot-password:hover {
          color: #f97316;
          transform: translateX(2px);
        }

        .error-message {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          color: #f87171;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          font-size: 0.875rem;
          margin-bottom: 1.5rem;
          text-align: left;
          animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
        }

        @keyframes shake {
          10%, 90% { transform: translate3d(-1px, 0, 0); }
          20%, 80% { transform: translate3d(2px, 0, 0); }
          30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
          40%, 60% { transform: translate3d(4px, 0, 0); }
        }

        .login-button {
          width: 100%;
          background: linear-gradient(to right, #f97316, #ea580c);
          color: white;
          border: none;
          padding: 1rem;
          border-radius: 99px;
          font-weight: 800;
          font-size: 1rem;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          box-shadow: 0 10px 30px rgba(249, 115, 22, 0.2);
          margin-top: 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          position: relative;
          overflow: hidden;
        }

        .login-button::after {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
          );
          transition: 0.5s;
        }

        .login-button:hover:not(:disabled)::after {
          left: 100%;
        }

        .login-button:hover:not(:disabled) {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(249, 115, 22, 0.3);
          background: linear-gradient(to right, #fb923c, #f97316);
        }

        .login-button:active:not(:disabled) {
          transform: translateY(0);
        }

        .login-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          background: #3f3f46;
          box-shadow: none;
        }

        .spinner {
          width: 1.25rem;
          height: 1.25rem;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .copyright-tag {
          position: absolute;
          bottom: 2rem;
          font-size: 0.75rem;
          font-weight: 700;
          color: #27272a;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          text-align: center;
          width: 100%;
          left: 0;
          animation: fade-in 2s ease-out forwards;
          opacity: 0;
        }

        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @media (max-width: 1024px) {
          .visual-panel { display: none; }
          .form-panel { flex: 1; padding: 2rem; border: none; }
          .foundry-modern-login { background: #030303; }
        }
      `}</style>

      {/* Left Panel: Welcome & Foundry Branding */}
      <div className="visual-panel">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
        <div className="shape shape-4"></div>
        <div className="glow-orb"></div>

        <div className="welcome-content">
          <h1>Welcome to Foundry</h1>
          <p>
            The enterprise-grade Internal Developer Platform.
            Streamlining infrastructure provisioning, compliance,
            and developer autonomy since 2024.
          </p>
        </div>
      </div>

      {/* Right Panel: Login Form (Dark Themed) */}
      <div className="form-panel">
        <div className="login-card">
          <div className="logo-mark animate-in">
            <Box color="white" size={28} />
          </div>

          <h2 className="animate-in delay-1">User Login</h2>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="input-group animate-in delay-2">
              <div className="input-wrapper">
                <User size={20} className="input-icon" />
                <input
                  type="text"
                  placeholder="Username / Email"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div className="input-group animate-in delay-3">
              <div className="input-wrapper">
                <Lock size={20} className="input-icon" />
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  className="eye-icon"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={loading}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="form-options animate-in delay-4">
              <label className="remember-me">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>Remember Me</span>
              </label>
              <a
                href="#"
                className="forgot-password"
                onClick={(e) => {
                  e.preventDefault();
                  appLogger.log('Forgot password clicked');
                }}
              >
                Forgot password?
              </a>
            </div>

            <div className="animate-in delay-5">
              <button type="submit" className="login-button" disabled={loading}>
                {loading ? (
                  <>
                    <div className="spinner"></div>
                    <span>Signing In...</span>
                  </>
                ) : (
                  'Sign In'
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="copyright-tag">
          © 2025 FOUNDRY IDP • ALL SYSTEMS OPERATIONAL
        </div>
      </div>
    </div>
  );
};
