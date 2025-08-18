<script>
    import { platform } from "../lib/utils.js";

    export let listName;
    export let timeStamp;
    export let selectedPlatform;
    export let listAttributes;
    export let isReviewed;
    export let progress;

    // Lookup platform details
    $: selectedDetails = platform.find((p) => p.name === selectedPlatform);
</script>

<div
    class="rounded-xl p-5 shadow-md bg-white  w-72 flex flex-col space-y-4 transition"
    style="border-color: {selectedDetails ? selectedDetails.color : 'white'}; border-style: solid; border-width: 1px;"
>


    <!-- Header -->
    <div class="flex justify-between items-center">
        {#if selectedDetails}
            <div class="flex flex-col items-center">
                <img
                    src={selectedDetails.img}
                    alt={selectedDetails.name}
                    class="w-8 h-8 rounded-full shadow"
                />
            </div>
        {/if}

        <div>
            <div class="text-base font-semibold text-gray-800">{listName}</div>
        </div>

        <!-- Platform Logo -->

        <div class="flex flex-col items-end space-y-1">
            {#if isReviewed}
                <span
                    class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-green-100 text-green-600"
                    >Reviewed</span
                >
            {:else}
                <span
                    class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-yellow-100 text-yellow-600"
                    >Pending</span
                >
            {/if}
        </div>
    </div>
    <div class="text-xs text-gray-500">
        {new Date(timeStamp).toLocaleString()}
    </div>
    <!-- Attributes -->
    <div class="space-y-2">
        {#each Object.entries(listAttributes) as [key, value]}
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">{key}</span>
                <span class="font-medium text-gray-900">{value}</span>
            </div>
        {/each}
    </div>

    <!-- Actions -->
    <div class="flex justify-center space-x-6 pt-2 border-t border-gray-100">
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
        >
            <i class="fa-solid fa-download"></i>
        </button>
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
        >
            <i class="fa-solid fa-edit"></i>
        </button>
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
        >
            <i class="fa-solid fa-trash"></i>
        </button>
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-yellow-600 hover:text-yellow-700 transition"
        >
            <img src="/images/rotate.gif" alt="loop" class="h-7 w-7" />
        </button>
    </div>

    <!-- Progress Bar -->
    <div class="space-y-1 py-3">
        <div class="flex justify-between text-xs text-gray-500">
            <span>Progress</span>
            <span>{progress}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
                class="h-2 rounded-full transition-all duration-500"
                style="width: {progress}%; background-color: {selectedDetails
                    ? selectedDetails.color
                    : '#3B82F6'}"
            ></div>
        </div>
    </div>

    <!-- Button styled with platform color -->
    <button
        class="w-full py-2 text-white rounded-lg font-semibold transition"
        style="background-color: {selectedDetails
            ? selectedDetails.color
            : '#4F46E5'}"
    >
        Start Audit
    </button>
</div>
