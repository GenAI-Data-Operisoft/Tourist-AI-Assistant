import React from 'react';
import ReactDOM from 'react-dom/client';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import App from './App';
import { amplifyConfig, isCognitoConfigured } from './authConfig';
import './index.css';

if (isCognitoConfigured) {
  Amplify.configure(amplifyConfig);
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {isCognitoConfigured ? (
      <Authenticator>
        {({ signOut, user }) => (
          <App authEnabled={true} signOut={signOut} user={user} />
        )}
      </Authenticator>
    ) : (
      <App authEnabled={false} />
    )}
  </React.StrictMode>,
);
