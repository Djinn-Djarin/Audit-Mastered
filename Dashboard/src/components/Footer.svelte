<script>
    import { getClientIP, getBackendIP } from "$lib/utils";
    import { onMount } from "svelte";
  
    import SystemModal from "../components/SystemModal.svelte"; // ✅ Use Component Instead of Inline Modal
    import { get } from "svelte/store";
  
    let clientIP = "127.0.0.1";
    let backendIP = "127.0.0.1";

    let showSystemMonitor = false;

  
    onMount(async () =>{
        clientIP = await getClientIP()
        backendIP = await getBackendIP()
        
    })
</script>

<!-- App Bar -->
<div
    class="w-full flex flex-col md:flex-row md:items-center md:justify-between gap-4 px-6 py-3 bg-white shadow-md border-b border-gray-200"
>
    <!-- Backend + Client IPs -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-6 gap-2 sm:gap-0">
        <div class="flex items-center space-x-2">
            <span class="font-medium text-gray-700 text-sm">Backend IP:</span>
            <span class="text-gray-900 text-sm">{backendIP}</span>
        </div>
        <div class="flex items-center space-x-2">
            <span class="font-medium text-gray-700 text-sm">User IP:</span>
            <span class="text-gray-900 text-sm">{clientIP}</span>
        </div>
    </div>

    <!-- Services -->
  

</div>
