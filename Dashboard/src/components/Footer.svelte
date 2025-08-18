<script>
    import { checkInternet } from "$lib/utils";

    import SystemModal from "../components/SystemModal.svelte"; // ✅ Use Component Instead of Inline Modal
    let celeryStatus = false;
    let redisStatus = true;
    const clientIP = "127.0.0.1";
    const backendIP = "127.0.0.1";

    let showSystemMonitor = false;
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
    <div class="flex flex-wrap items-center gap-4">
        <!-- Celery -->
        <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700">Celery</span>
            <div
                class={`h-3.5 w-3.5 rounded-full border-2 border-white shadow-sm ${
                    celeryStatus ? "bg-green-700 animate-pulse" : "bg-red-500"
                }`}
            ></div>
        </div>
        <!-- Redis -->
        <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700">Redis</span>
            <div
                class={`h-3.5 w-3.5 rounded-full border-2 border-white shadow-sm ${
                    redisStatus ? "bg-green-700 animate-pulse" : "bg-red-500"
                }`}
            ></div>
        </div>
    </div>

</div>
