// +layout.server.ts
import { redirect } from '@sveltejs/kit';

export const load = async ({ cookies, url }) => {
  // don’t block login page
  if (url.pathname === '/login') return;

  const access = cookies.get('access');

  if (!access) {
    throw redirect(303, '/login');
  }

  return {};
};
