<script>
    import { loginUser, me } from "$lib/utils.js";

    let username = "Devendra";
    let password = "Kuber@121";
    let error = "";
    let user = null;

    async function handleLogin(event) {
        event.preventDefault();

        const result = await loginUser(username, password);

        if (result.error) {
            error = result.error;
            return;
        }

        user = await me();
        // console.log(user, "user");
    }
</script>

<div class="flex min-h-screen">
    <!-- Left image side -->
    <div class="w-3/5 relative hidden md:block">
        <img
            src="/images/bird.jpg"
            alt="Login Background"
            class="object-cover w-full h-full"
        />
        <!-- Optional overlay for better text contrast -->
        <!-- <div class="absolute inset-0 bg-black/30"></div> -->
    </div>

    <!-- Right login card -->
    <div class="w-full md:w-2/5 flex items-center justify-center bg-white">
        <form
            on:submit|preventDefault={handleLogin}
            class=" flex flex-col bg-gray-100 p-10 rounded-xl shadow-sm w-full max-w-md space-y-6"
        >
        

            {#if error}
                <p class="text-sm text-black text-center">{error}</p>
            {/if}

            <div>
           
                <input
                    type="text"
                    bind:value={username}
                    required
                    class="mt-1 block w-full px-4 py-2 border border-gray-300  rounded-lg focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
                />
            </div>

            <div>
        
                <input
                    type="password"
                    bind:value={password}
                    required
                    class="mt-1 block w-full px-4 py-2 border  border-gray-300 rounded-lg  focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black bg-white"
                />
            </div>

            <button
                type="submit"
                class="w-32 mx-auto bg-gray-300 text-black py-2 rounded-lg font-medium "
            >
                Login
            </button>
        </form>
    </div>
</div>

<style>
    /* Optional: make the left image full height and cover */
    @media (min-width: 768px) {
        .object-cover {
            height: 100vh;
        }
    }

    a{
        color: #ac5838;
        color: #ac5938b4;
    }
</style>
