export const cognitoConfig = {
  region: import.meta.env.VITE_COGNITO_REGION,
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
  domain: import.meta.env.VITE_COGNITO_DOMAIN,
  redirectSignIn: import.meta.env.VITE_COGNITO_REDIRECT_SIGN_IN,
  redirectSignOut: import.meta.env.VITE_COGNITO_REDIRECT_SIGN_OUT,
};

export const isCognitoConfigured = Boolean(
  cognitoConfig.region &&
    cognitoConfig.userPoolId &&
    cognitoConfig.userPoolClientId &&
    cognitoConfig.domain &&
    cognitoConfig.redirectSignIn &&
    cognitoConfig.redirectSignOut,
);

export const amplifyConfig = {
  Auth: {
    Cognito: {
      userPoolId: cognitoConfig.userPoolId,
      userPoolClientId: cognitoConfig.userPoolClientId,
      loginWith: {
        oauth: {
          domain: cognitoConfig.domain,
          scopes: ['openid', 'email', 'profile'],
          redirectSignIn: [cognitoConfig.redirectSignIn],
          redirectSignOut: [cognitoConfig.redirectSignOut],
          responseType: 'code',
        },
      },
    },
  },
};
