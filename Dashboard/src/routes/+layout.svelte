<!-- Dashboard/src/routes/+layout.svelte -->
<script>
	import "../app.css";
	import favicon from "$lib/assets/favicon.svg";
	let { children } = $props();
	
	import { onMount } from "svelte";
	import { TokenService } from "$lib/utils";
    import { on } from "svelte/events";
	
	onMount(() => {
		if (window.location.pathname === "/login") return;
		const accessToken = TokenService.getAccessToken();
		
		if (!accessToken) {
			// Redirect unauthenticated users to login
			window.location.href = "/login";
		}
	});


</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}
