<script>
  import "../app.css";
  import favicon from "$lib/assets/cat.jpg";
  import { Toaster } from "svelte-sonner";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { TokenService } from "$lib/utils"; 

  let { children } = $props();

 
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<Toaster position="top-right" richColors />
{@render children?.()}
