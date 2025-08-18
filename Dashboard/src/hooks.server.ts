// src/hooks.server.ts
import jwt from 'jsonwebtoken';
import { ServerTokenService } from '$lib/services/ServerTokenServices';

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
    const tokenService = new ServerTokenService(event.cookies);
    const access = tokenService.getAccessToken();

    event.locals.user = null;

    if (access) {
        try {
            // Verify and decode JWT
            const payload = jwt.verify(access, process.env.JWT_SECRET);
            // Store only necessary info in locals
            event.locals.user = {
                id: payload.user_id,
                username: payload.username,
                token: access
            };
        } catch (err) {
            // JWT invalid or expired, try refresh
            const newAccess = await tokenService.refreshAccessToken();
            if (newAccess) {
                try {
                    const payload = jwt.verify(newAccess, process.env.JWT_SECRET);
                    event.locals.user = {
                        id: payload.user_id,
                        username: payload.username,
                        token: newAccess
                    };
                } catch {
                    event.locals.user = null;
                }
            }
        }
    }

    return resolve(event);
}
