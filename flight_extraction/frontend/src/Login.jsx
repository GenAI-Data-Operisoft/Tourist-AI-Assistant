import { useState } from 'react';
import { LogIn, Loader2, AlertCircle } from 'lucide-react';
import tourishLogo from './assets/tourish-logo.png';
import loginBanner from './assets/banner.png';

const COGNITO_REGION = import.meta.env.VITE_COGNITO_REGION;
const COGNITO_CLIENT_ID = import.meta.env.VITE_COGNITO_APP_CLIENT_ID;

function Login({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `https://cognito-idp.${COGNITO_REGION}.amazonaws.com/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
          },
          body: JSON.stringify({
            AuthFlow: 'USER_PASSWORD_AUTH',
            ClientId: COGNITO_CLIENT_ID,
            AuthParameters: { USERNAME: username, PASSWORD: password },
          }),
        }
      );

      const data = await response.json();
      
      if (data.AuthenticationResult) {
        localStorage.setItem('token', data.AuthenticationResult.AccessToken);
        localStorage.setItem('username', username);
        onSuccess(username);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Login failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'row'
    }}>
      {/* Left Side - Login Form (White Background) */}
      <div style={{
        flex: '0 0 45%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'white',
        padding: '40px'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '480px',
          background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
          padding: '48px',
          borderRadius: '16px',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
          border: '1px solid #bae6fd'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <img 
              src={tourishLogo} 
              alt="Tourish Logo" 
              style={{ 
                width: '200px', 
                height: 'auto', 
                marginBottom: '32px',
                display: 'block',
                marginLeft: 'auto',
                marginRight: 'auto'
              }} 
            />
            <h2 style={{ 
              margin: '0 0 12px 0', 
              fontSize: '28px',
              color: '#1f2937',
              fontWeight: '700',
              letterSpacing: '0.5px'
            }}>
              TOURISH AI ASSISTANT
            </h2>
            <p style={{ color: '#6b7280', margin: 0, fontSize: '15px' }}>
              Sign in to continue
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '15px',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '15px',
                  transition: 'border-color 0.2s',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>

            {error && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#dc2626',
                marginBottom: '24px',
                fontSize: '14px'
              }}>
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px',
                background: '#0c4a6e',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s',
                boxShadow: '0 4px 12px rgba(12, 74, 110, 0.3)'
              }}
              onMouseEnter={(e) => !loading && (e.target.style.background = '#075985')}
              onMouseLeave={(e) => e.target.style.background = '#0c4a6e'}
            >
              {loading ? (
                <>
                  <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Sign In
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Right Side - Banner Image */}
      <div style={{
        flex: '0 0 55%',
        backgroundImage: `url(${loginBanner})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}>
      </div>
    </div>
  );
}

export default Login;
