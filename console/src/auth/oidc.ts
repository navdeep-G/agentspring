import { UserManager, WebStorageStateStore, Log } from "oidc-client-ts";
export function makeManager(config: {authority: string, client_id: string, redirect_uri: string}){
  Log.setLogger(console);
  return new UserManager({ authority: config.authority, client_id: config.client_id, redirect_uri: config.redirect_uri, response_type: "code", scope: "openid profile email", userStore: new WebStorageStateStore({ store: window.localStorage }) });
}
export async function login(um: UserManager){ await um.signinRedirect(); }
export async function handleRedirect(um: UserManager){ const user = await um.signinRedirectCallback(); return user; }
export async function getToken(um: UserManager){ const user = await um.getUser(); return user?.id_token || user?.access_token; }
