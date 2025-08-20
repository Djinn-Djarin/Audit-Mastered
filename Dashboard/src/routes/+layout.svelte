<script lang="ts">
  import "../app.css";
  import favicon from "$lib/assets/cat.png";
  import { Toaster } from "svelte-sonner";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { TokenService } from "$lib/utils";

  let { children } = $props();

  onMount(async () => {
    if (window.location.pathname === "/login") return;

    let access = TokenService.getAccessToken();

    if (!access) {
      goto("/login");
      return;
    }

    const refreshed = await TokenService.refreshAccessToken();
    if (!refreshed) {
      TokenService.clearTokens();
      goto("/login");
    }
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<Toaster position="top-right" richColors />
{@render children?.()}
