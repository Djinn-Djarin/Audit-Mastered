<script>
    import { createEventDispatcher } from "svelte";

    import { platforms, addListName, addItemsToList } from "../lib/utils.js";
    import { toast } from "svelte-sonner";

    const dispatch = createEventDispatcher();
    let listName = "Etrade";
    let selectedPlatform = "amazon";
    let file = null;

    function handleFileChange(e) {
        file = e.target.files[0];
    }

    async function handleSubmit() {
        try {
            if (!file) {
                toast.error("Please Upload File");
                return;
            }
            const addList = await addListName(listName, selectedPlatform);
            console.log("addListName:", addList);

            if (addList.status !== "success") {
                toast.error(`Failed to create list: ${listName}`);
                return;
            }

            toast.success(`${listName} List created!`);

            const listId = addList.list_id;

            // Upload file if it exists
            let addItems;
            if (listId && file) {
                addItems = await addItemsToList(listId, file);
                console.log("addItems:", addItems);

                if (addItems?.status !== "success") {
                    toast.error(
                        addItems?.msg ||
                            "File upload failed. List created without items.",
                    );
                }
            }

            // Build the object to send to parent
            const newList = {
                list_id: listId,
                list_name: listName,
                created_at: new Date().toISOString(), // or use returned value from API
                platform: selectedPlatform,
                list_attributes: {
                    product_count: file ? addItems.product_count : 0, // or actual count if API returns it
                    count: 0, // or actual count if API returns it
                    "Processed Items":0
                },
            };

            // Dispatch both close and the new list to parent
            dispatch("add", newList);
            dispatch("close");
        } catch (err) {
            console.error("API request failed:", err);

            let msg = "Request failed";
            try {
                const errObj = JSON.parse(err.message);
                msg = errObj.msg || msg;
            } catch (e) {
                msg = err.message; // fallback to raw error message
            }

            toast.error(msg);
        }
    }

    // get platform details
    $: selectedDetails = platforms.find((p) => p.name === selectedPlatform);
</script>

<div
    class="rounded-xl p-6 shadow-lg border border-gray-200 w-[500px] flex flex-col space-y-5 transition"
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
            {#each platforms as p}
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
    <div class="flex flex-col">
     <span class="text-xs bg-gray-600 p-2 space-y-2 flex flex-col text-gray-100 font-mono rounded">

        <span>
            Column name must be the same as the platform. <br>
        </span>
        <span>

            <span class="bg-gray-700 text-white font-mono rounded px-2 py-0.5 ml-1">
                amazon
            </span>
            <span class="bg-gray-700 text-white font-mono rounded px-2 py-0.5 ml-1">
                flipkart
            </span>
            <span class="bg-gray-700 text-white font-mono rounded px-2 py-0.5 ml-1">
                zepto
            </span>
            <span class="bg-gray-700 text-white font-mono rounded px-2 py-0.5 ml-1">
                swiggy
            </span>
        </span>

</span>


        <label class="block text-sm font-medium text-gray-700 m-2"
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
