<script>
    import { loginUser } from "$lib/utils.js";

    import { me } from "$lib/utils";
    let username = "Devendra";
    let password = "Kuber@121";
    let error = "";
    let user = null;

    async function handleLogin(event) {
        event.preventDefault();

        const result = await loginUser(username, password);

        if (result.error) {
            error = result.error;
        }
        user = await me();
        console.log(user, "user");
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <form
        on:submit|preventDefault={handleLogin}
        class="bg-white p-8 rounded-xl shadow-md w-full max-w-sm space-y-4"
    >
        <h1 class="text-2xl font-bold text-gray-800 text-center">Login</h1>

        {#if error}
            <p class="text-sm text-red-500 text-center">{error}</p>
        {/if}

        <div>
            <label class="block text-sm font-medium text-gray-700"
                >Username</label
            >
            <input
                type="text"
                bind:value={username}
                class="mt-1 block w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
            />
        </div>

        <div>
            <label class="block text-sm font-medium text-gray-700"
                >Password</label
            >
            <input
                type="password"
                bind:value={password}
                class="mt-1 block w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
            />
        </div>

        <button
            type="submit"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition"
        >
            Login
        </button>
    </form>
</div>
