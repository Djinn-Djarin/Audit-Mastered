<script>
    import { onMount } from "svelte";

    export let show = false;
    export let title = "System Monitor";
    export let onClose;

    // Static props (you can still pass them from parent)
    export let clientIP = "127.0.0.1";
    export let backendIP = "127.0.0.1";
    export let celeryStatus = false;
    export let redisStatus = true;

    // Dynamic system stats from backend
    let stats = {
        cpu: "Loading...",
        ram: "Loading...",
        disk: "Loading...",
        network: "Loading...",
        cors: "Loading..."
    };

    function closeModal() {
        if (onClose) onClose();
    }

    function handleKeydown(e) {
        if (e.key === "Escape") closeModal();
    }

    onMount(async () => {
        try {
            const res = await fetch("/api/system-stats"); // backend endpoint (FastAPI/Flask)
            if (res.ok) {
                stats = await res.json();
            }
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    });
</script>

{#if show}
    <div 
        class="fixed inset-0 flex items-center justify-center z-50"
        on:keydown={handleKeydown}
        tabindex="0"
    >
        <!-- Overlay -->
        <button
            type="button"
            aria-label="Close modal overlay"
            class="absolute inset-0 bg-gray-200 bg-opacity-50"
            on:click={closeModal}
        ></button>

        <!-- Modal -->
        <div
            class="relative z-10 bg-white rounded-2xl shadow-xl max-w-2xl w-full mx-4 p-6 overflow-y-auto max-h-[90vh] transition transform scale-95 animate-fade-in"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <!-- Header -->
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h2 id="modal-title" class="text-xl font-semibold text-gray-800">{title}</h2>
                <button
                    type="button"
                    aria-label="Close modal"
                    on:click={closeModal}
                    class="text-gray-500 hover:text-gray-800 transition"
                >
                    ✕
                </button>
            </div>

            <!-- Body -->
            <div class="space-y-3">
                <!-- Existing Static Info -->
                <div class="flex justify-between border-b py-1 text-sm">
                    <span class="text-gray-600 font-medium">Client IP</span>
                    <span class="text-gray-900">{clientIP}</span>
                </div>
                <div class="flex justify-between border-b py-1 text-sm">
                    <span class="text-gray-600 font-medium">Backend IP</span>
                    <span class="text-gray-900">{backendIP}</span>
                </div>
                <div class="flex justify-between border-b py-1 text-sm">
                    <span class="text-gray-600 font-medium">Celery</span>
                    <span class={`px-2 py-0.5 rounded text-white text-xs ${celeryStatus ? "bg-green-600" : "bg-red-600"}`}>
                        {celeryStatus ? "Running" : "Stopped"}
                    </span>
                </div>
                <div class="flex justify-between border-b py-1 text-sm">
                    <span class="text-gray-600 font-medium">Redis</span>
                    <span class={`px-2 py-0.5 rounded text-white text-xs ${redisStatus ? "bg-green-600" : "bg-red-600"}`}>
                        {redisStatus ? "Running" : "Stopped"}
                    </span>
                </div>

                <!-- Dynamic System Stats -->
                {#each Object.entries(stats) as [key, value]}
                    <div class="flex justify-between border-b py-1 text-sm">
                        <span class="text-gray-600 font-medium capitalize">{key}</span>
                        <span class="text-gray-900">{value}</span>
                    </div>
                {/each}
            </div>

            <!-- Footer -->
            <div class="mt-6 flex justify-end">
                <button
                    type="button"
                    on:click={closeModal}
                    class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                    Close
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    @keyframes fade-in {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    .animate-fade-in {
        animation: fade-in 0.2s ease-out;
    }
</style>
