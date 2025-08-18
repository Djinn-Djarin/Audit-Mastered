// src/routes/protected/+page.server.ts
import { redirect } from '@sveltejs/kit';

export async function load({ locals }) {
    if (!locals.user) {
        throw redirect(302, '/login');
    }

    // Use locals.user directly
    return { user: locals.user };
}
