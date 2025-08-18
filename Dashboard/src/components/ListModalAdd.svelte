<script>
    import { platform } from "../lib/utils.js";
 import { ApiService } from "../lib/utils.js";

    let listName = "My Product List";
    let selectedPlatform = "amazon";
    let file = null;

    function handleFileChange(e) {
        file = e.target.files[0];
        // Handle form submission
    }



async function handleSubmit() {
    try {
        const data = await ApiService.post(
            "http://127.0.0.1:8000/api/create_product_list/",
            {
                name: listName,
                platform: selectedPlatform,
                file: file ? file.name : null,
            }
        );
        console.log("Success:", data);
    } catch (err) {
        console.error("API request failed:", err);
    }
}


    // get platform details
    $: selectedDetails = platform.find((p) => p.name === selectedPlatform);
</script>

<div
    class="rounded-xl p-6 shadow-lg border border-gray-200 w-96 flex flex-col space-y-5 transition"
    style="background-color: {selectedDetails
        ? selectedDetails.color + '20'
        : 'white'}"
>
    <!-- List Name -->
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
            >List Name</label
        >
        <input
            type="text"
            placeholder="Enter list name"
            bind:value={listName}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
    </div>

    <!-- Platform -->
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
            >Platform</label
        >
        <select
            bind:value={selectedPlatform}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
            <option value="" disabled>Select a platform</option>
            {#each platform as p}
                <option value={p.name}>{p.name}</option>
            {/each}
        </select>
    </div>

    {#if selectedDetails}
        <div class="flex items-center space-x-3">
            <img
                src={selectedDetails.img}
                alt={selectedDetails.name}
                class="w-8 h-8 rounded-full shadow"
            />
            <span class="font-semibold capitalize">{selectedDetails.name}</span>
        </div>
    {/if}

    <!-- Upload File -->
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
            >Upload File</label
        >
        <label
            class="flex items-center justify-center px-4 py-3 border border-dashed border-gray-400 rounded-lg cursor-pointer hover:bg-gray-50 transition"
        >
            <input type="file" class="hidden" on:change={handleFileChange} />
            <span class="text-sm text-gray-600"
                >{file ? file.name : "Choose a file"}</span
            >
        </label>
    </div>

    <!-- Submit Button -->
    <button
        on:click={handleSubmit}
        class="w-full py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
    >
        Add List
    </button>
</div>
