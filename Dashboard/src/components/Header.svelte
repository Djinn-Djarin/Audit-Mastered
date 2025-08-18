<script>
    import { checkInternet } from "$lib/utils";
    import { handleLogout } from "$lib/utils";
    import { onDestroy } from "svelte";
    import { goto } from "$app/navigation";

    let userImg = "/images/boy.png";
    let userName = ""; // dynamic username
    let isLoggedIn = false;
    let isInternetConnected = false;

    async function updateInternetStatus() {
        isInternetConnected = await checkInternet();
    }

    updateInternetStatus();
    const interval = setInterval(updateInternetStatus, 1000);
    onDestroy(() => clearInterval(interval));

    function goToLogin() {
        goto("/login"); // navigate to login page
    }
</script>

<div
    class={`w-full flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-4 sm:px-8 py-3 ${
        isInternetConnected ? "bg-white" : "bg-red-500 animate-pulse"
    } shadow-md border-b border-gray-200`}
>
    <!-- Left Section (Internet status) -->
    <div class="flex items-center space-x-2 sm:space-x-3">
        <span class="text-sm font-medium text-gray-700">Internet</span>
        <div
            class={`h-3.5 w-3.5 rounded-full ${
                isInternetConnected ? "bg-green-700 animate-pulse" : "bg-red-500"
            }`}
        ></div>
    </div>

    <!-- Right Section -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-6 gap-3 sm:gap-0">
        {#if isLoggedIn}
            <!-- User Info -->
            <div class="flex items-center space-x-3">
                <div class="h-10 w-10 rounded-full overflow-hidden shadow-sm ring-2 ring-gray-200 flex-shrink-0">
                    <img src={userImg} alt="User avatar" class="h-full w-full object-cover" />
                </div>
                <div class="text-gray-800 font-medium text-sm truncate max-w-[120px] sm:max-w-none">
                    {userName}
                </div>
            </div>

            <!-- Logout -->
            <button
                class="px-4 py-1.5 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-md shadow-sm transition-colors w-full sm:w-auto"
                on:click={handleLogout}
            >
                Logout
            </button>
        {:else}
            <!-- Login Button -->
            <button
                class="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-colors w-full sm:w-auto"
                on:click={goToLogin}
            >
                Login
            </button>
        {/if}
    </div>
</div>
