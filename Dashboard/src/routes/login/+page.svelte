<script>
  import { onMount, onDestroy } from "svelte";
  import Walking from "../../components/Walking.svelte";
  import { loginUser, me } from "$lib/utils.js";

  let src = [
  
    "/images/Moody Dog.json",
    "/images/Moody Giraffe.json",
  ];

  let currentSrc = src[0];
  let index = 0;

  // Use onMount to ensure reactivity inside Svelte
  onMount(() => {
    const interval = setInterval(() => {
      index = (index + 1) % src.length;
      currentSrc = src[index]; // reassign triggers update
    }, 5000);

    onDestroy(() => clearInterval(interval));
  });

  let username = "";
  let password = "";
  let error = "";
  let user = null;

  async function handleLogin(event) {
    event.preventDefault();
    const result = await loginUser(username, password);
    if (result.error) {
      error = result.error;
      return;
    }
  }
</script>




<svelte:head>
    <title>Kuber Audit Login</title>
</svelte:head>

<div class="relative h-screen w-screen overflow-hidden">
  <!-- Fullscreen Walking -->
  <div class="absolute ">
    <Walking src={currentSrc} />
  </div>

  <!-- Login card -->
  <div class="absolute right-10 top-1/2 -translate-y-1/2 flex items-center justify-center">
    <form
      on:submit|preventDefault={handleLogin}
      class="flex flex-col bg-white p-10 rounded-xl w-96 max-w-md space-y-6"
    >
      {#if error}
        <p class="text-sm text-red-600 text-center">{error}</p>
      {/if}

      <div>
        <input
          type="text"
          bind:value={username}
          required
          placeholder="username"
          class="mt-1 block w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
        />
      </div>

      <div>
        <input
          type="password"
          bind:value={password}
          required
          placeholder="password"
          class="mt-1 block w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
        />
      </div>

      <button
        type="submit"
        class="w-32 mx-auto bg-[#41636d] border border-gray-200 text-white py-2 rounded-lg font-medium"
      >
        Login
      </button>
    </form>
  </div>
</div>


