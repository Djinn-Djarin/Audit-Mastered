<script>
    import { onMount } from "svelte";
    import ListModalAdd from "../components/ListModalAdd.svelte";
    import ListModalStatus from "../components/ListModalStatus.svelte";
    import Header from "../components/Header.svelte";
    import Footer from "../components/Footer.svelte";

    import { getAllLists, auditTaskIDs } from "$lib/utils";

    // export let data;
    // const { lists } = data;

    let lists = [];
    let isAddList = false;

    function toggleAddList() {
        isAddList = !isAddList;
    }

    onMount(async () => {
        let result = await getAllLists();
        lists = result.data;
        // console.log(lists, "user lists");
    });

    function handleDeleted(event) {
        const { list_id } = event.detail;
        // Remove the deleted list from the array
        lists = lists.filter((list) => list.list_id !== list_id);
    }

    onMount(async () => {
        const res = await auditTaskIDs(); // calls RunningAudits API
        console.log("Running audits from backend:", res);

        if (res?.running_audits?.length > 0) {
            localStorage.setItem(
                "audit_tasks",
                JSON.stringify(res.running_audits),
            );
        } else {
            localStorage.removeItem("audit_tasks");
        }
    });
</script>

<svelte:head>
     <title>Kuber Audit Panel</title>
</svelte:head>

<div class="flex flex-col min-h-screen bg-gray-100">
    <!-- Header always on top -->
    <Header />

    <!-- Main content grows to push footer down -->
    <main
        class="flex-1 flex flex-wrap gap-15 px-6 py-10 items-start justify-center"
    >
        {#if lists.length > 0}
            {#each lists as list (list.list_id)}
                <ListModalStatus {...list} on:deleted={handleDeleted} />
            {/each}
        {:else}
            <p>Create a list</p>
        {/if}
    </main>

  <div class="fixed bottom-[20%] right-[50%]">
    <button
        on:click={toggleAddList}
        class="rounded-full h-20 w-20 flex items-center justify-center shadow-xl bg-gray-200 transition border border-dashed border-gray-400 
               "
    >
        <img
            src="/images/plus.png"
            alt="Add list"
            class="w-10 h-10 "
        />
    </button>
</div>


    <!-- Modal Overlay -->
    {#if isAddList}
        <div class="fixed inset-0 flex items-center justify-center z-50">
            <!-- Overlay background -->
            <div
                class="absolute inset-0 bg-gray-400/80 shadow-lg"
                on:click={() => (isAddList = false)}
            ></div>

            <!-- Modal Content -->
            <div class="relative z-10">
                <div class="bg-white rounded-lg p-6">
                    <ListModalAdd
                        on:close={() => (isAddList = false)}
                        on:add={(e) => (lists = [...lists, e.detail])}
    
                        
                    />
                </div>
            </div>
        </div>
    {/if}

    <!-- Footer always pinned to bottom -->
    <Footer />
</div>

