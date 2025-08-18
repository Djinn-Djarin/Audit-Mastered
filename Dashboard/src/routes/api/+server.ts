// src/routes/api/logout/+server.ts
import { json } from '@sveltejs/kit';

export async function POST({ cookies }) {
    cookies.delete('access');
    cookies.delete('refresh');
    return json({ success: true });
}
